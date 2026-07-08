from types import SimpleNamespace

import pytest

from app.agents.guardrails.qualification import evaluate_gates
from app.agents.prompts.outreach import OUTREACH_DRAFT_INSTRUCTIONS
from app.agents.tools.public_data import create_census_tool
from app.agents.utils.scoring import load_scoring_config, score_lead
from app.core.config import Settings
from app.infrastructure.llm.factory import clear_llm_provider_cache, get_llm_provider
from app.infrastructure.llm.litellm import LiteLLMProvider
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.infrastructure.public_data.types import CensusMarketSnapshot
from app.schemas.lead import LeadCreate


def _lead() -> LeadCreate:
    return LeadCreate(
        contact_name="Sample Contact",
        email="sample@operator.example",
        company="Multifamily Operator",
        role="VP Leasing",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
    )


def _draft_kwargs(settings: Settings):
    lead = _lead()
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    gates = evaluate_gates(lead, enrichment)
    score = score_lead(
        lead,
        gates,
        enrichment,
        config=load_scoring_config(settings),
    )
    return {
        "lead": lead,
        "gates": gates,
        "enrichment": enrichment,
        "score": score,
        "talking_points": ["Use market context."],
        "instructions": OUTREACH_DRAFT_INSTRUCTIONS,
        "tools": [],
        "public_data_client": object(),
    }


@pytest.mark.asyncio
async def test_litellm_provider_calls_configured_proxy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    async def fake_acompletion(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Model-backed outreach draft")
                )
            ]
        )

    monkeypatch.setattr("litellm.acompletion", fake_acompletion)
    settings = Settings(
        llm_model="signal-chat",
        litellm_api_base="http://localhost:4000",
        litellm_api_key="sk-test",
    )
    result = await LiteLLMProvider(settings).draft_outreach(**_draft_kwargs(settings))

    assert result.draft is not None
    assert result.draft.body == "Model-backed outreach draft"
    assert result.draft.sources == _draft_kwargs(settings)["enrichment"].sources
    assert captured["model"] == "openai/signal-chat"
    assert captured["api_base"] == "http://localhost:4000"
    assert captured["api_key"] == "sk-test"
    assert captured["temperature"] == 0.2
    assert captured["messages"][0]["role"] == "system"
    system_content = captured["messages"][0]["content"]
    assert "<role>" in system_content
    assert "inbound multifamily lead" in system_content
    assert "Use only supplied context or returned tool source facts" in system_content
    assert "Do not change, question, or recalculate score, tier, gates" in (
        system_content
    )
    assert "Do not include raw email addresses" in system_content
    assert captured["messages"][1]["role"] == "user"
    user_content = captured["messages"][1]["content"]
    assert "Context:" in user_content
    assert (
        "Do not change score, tier, gates, or sales insights in talking_points."
        in user_content
    )
    assert "sample@" not in user_content
    assert "***@operator.example" in user_content


@pytest.mark.asyncio
async def test_litellm_provider_returns_none_for_empty_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_acompletion(**kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
        )

    monkeypatch.setattr("litellm.acompletion", fake_acompletion)
    settings = Settings()
    result = await LiteLLMProvider(settings).draft_outreach(**_draft_kwargs(settings))

    assert result.draft is None


@pytest.mark.asyncio
async def test_litellm_provider_executes_bounded_tool_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []

    async def fake_acompletion(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=None,
                            tool_calls=[
                                SimpleNamespace(
                                    id="call_1",
                                    type="function",
                                    function=SimpleNamespace(
                                        name="fetch_census_market_demographics",
                                        arguments='{"city":"Austin","state":"TX"}',
                                    ),
                                )
                            ],
                        )
                    )
                ]
            )
        return SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content="Draft with research"))
            ]
        )

    class FakePublicDataClient:
        async def census_market_snapshot(self, **kwargs):
            return CensusMarketSnapshot(renter_share=0.64, median_rent=1925)

    monkeypatch.setattr("litellm.acompletion", fake_acompletion)
    settings = Settings(agent_research_max_tool_rounds=1)
    kwargs = _draft_kwargs(settings)
    kwargs["tools"] = [create_census_tool()]
    kwargs["public_data_client"] = FakePublicDataClient()

    result = await LiteLLMProvider(settings).draft_outreach(**kwargs)

    assert result.draft is not None
    assert result.tool_call_names == ("fetch_census_market_demographics",)
    assert "tools" in calls[0]
    assert calls[1]["tools"] is None
    tool_message = next(
        message for message in calls[1]["messages"] if message["role"] == "tool"
    )
    assert "Renter share" in tool_message["content"]
    assert any(source.value == "64%" for source in result.draft.sources)


def test_llm_provider_factory_caches_by_backend_env_shape() -> None:
    clear_llm_provider_cache()
    settings = Settings(
        llm_model="signal-chat",
        litellm_api_base="http://localhost:4000",
        litellm_api_key="sk-test",
    )

    first = get_llm_provider(settings)
    same = get_llm_provider(settings)
    changed = get_llm_provider(settings.model_copy(update={"llm_model": "other"}))

    assert first is same
    assert changed is not first
    clear_llm_provider_cache()
