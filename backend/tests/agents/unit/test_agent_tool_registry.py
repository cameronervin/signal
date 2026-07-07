from app.agents.chains.outreach_drafting import OUTREACH_DRAFT_CHAIN
from app.agents.tools.tool_assignment import (
    build_prompt_bindings,
    build_workflow_chain_tool_map,
    resolve_active_tools,
)
from app.agents.tools.tool_prompts import ToolPromptKey
from app.agents.tools.tool_registry import (
    TOOL_REGISTRY,
    WORKFLOW_CHAIN_NAMES,
    ToolBuildContext,
)
from app.core.config import Settings


def test_research_tool_registry_declares_stable_tool_order() -> None:
    assert WORKFLOW_CHAIN_NAMES == {
        "signal_pipeline": (OUTREACH_DRAFT_CHAIN,),
    }
    assert [spec.tool_name for spec in TOOL_REGISTRY] == [
        "geocode_property_address",
        "fetch_census_market_demographics",
        "fetch_datausa_household_growth",
        "fetch_fred_market_economics",
        "lookup_news_company_trigger",
        "lookup_wikipedia_company_background",
        "validate_email_domain_mx",
    ]


def test_research_tool_assignment_respects_keys_and_settings() -> None:
    no_keys = ToolBuildContext(settings=Settings(fred_api_key=None, news_api_key=None))
    no_key_tools = resolve_active_tools(no_keys)

    assert [tool.name for tool in no_key_tools] == [
        "geocode_property_address",
        "fetch_census_market_demographics",
        "fetch_datausa_household_growth",
        "lookup_wikipedia_company_background",
        "validate_email_domain_mx",
    ]

    keyed = ToolBuildContext(
        settings=Settings(fred_api_key="fred-key", news_api_key="news-key")
    )
    keyed_tools = resolve_active_tools(keyed)
    assignments = build_workflow_chain_tool_map(keyed_tools)

    assigned_names = [
        tool.name for tool in assignments["signal_pipeline"][OUTREACH_DRAFT_CHAIN]
    ]
    assert assigned_names == [
        "geocode_property_address",
        "fetch_census_market_demographics",
        "fetch_datausa_household_growth",
        "fetch_fred_market_economics",
        "lookup_news_company_trigger",
        "lookup_wikipedia_company_background",
        "validate_email_domain_mx",
    ]

    disabled_tools = resolve_active_tools(
        ToolBuildContext(settings=Settings(agent_research_tools_enabled=False))
    )
    assert disabled_tools == []


def test_prompt_bindings_include_only_active_tool_snippets() -> None:
    active = build_prompt_bindings(["fetch_census_market_demographics"])

    key = ToolPromptKey(OUTREACH_DRAFT_CHAIN, "fetch_census_market_demographics")
    assert set(active) == {key}
    assert "renter share" in active[key]
    assert build_prompt_bindings([]) == {}
