import pytest

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.agents.graph_provider import SignalGraphProvider, SignalGraphProviderCache
from app.core.config import Settings
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.lead import LeadCreate


class FakePublicDataClient:
    def __init__(self) -> None:
        self.calls = 0

    async def enrich(self, lead: LeadCreate):
        self.calls += 1
        return demo_enrichment(lead.company, lead.city, lead.state)


def test_signal_graph_provider_reuses_compiled_graph() -> None:
    provider = SignalGraphProvider(settings=Settings())

    assert provider.signal_graph() is provider.signal_graph()


def test_signal_graph_provider_cache_replaces_when_settings_change() -> None:
    cache = SignalGraphProviderCache()

    first = cache.get_or_create(settings=Settings(env="one"))
    same = cache.get_or_create(settings=Settings(env="one"))
    changed = cache.get_or_create(settings=Settings(env="two"))

    assert first is same
    assert changed is not first


@pytest.mark.asyncio
async def test_executor_injects_public_data_context() -> None:
    public_data_client = FakePublicDataClient()
    executor = SignalPipelineExecutor(
        settings=Settings(),
        public_data_client=public_data_client,
    )
    lead = LeadCreate(
        contact_name="Sarah Chen",
        email="sarah@meridianresidential.example",
        company="Meridian Residential",
        role="VP Leasing",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
    )

    result = await executor.execute(
        {
            "lead_id": "lead_test",
            "run_id": "run_test",
            "lead": lead,
            "activity_log": ["api_insert: lead received"],
        }
    )

    assert public_data_client.calls == 1
    assert result["gates"].status == "passed"
    assert result["score"].tier == "A"
