import pytest

from app.agents.graph_provider import (
    clear_signal_graph_provider_cache,
    get_signal_graph_provider,
)
from app.core.config import Settings
from app.infrastructure.public_data import create_public_data_client
from app.repositories.postgres import PostgresSignalRepository
from app.services.lead_service import get_lead_service


@pytest.mark.asyncio
async def test_lead_service_dependency_uses_app_state_resources() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://postgres:test/db",
        llm_model="state-scoped-model",
    )
    context = FakeSessionContext()
    public_data_client = create_public_data_client(settings)
    graph_provider = get_signal_graph_provider(settings=settings)
    request = FakeRequest(
        settings=settings,
        sessionmaker=context,
        public_data_client=public_data_client,
        signal_graph_provider=graph_provider,
    )

    service_generator = get_lead_service(request, settings)
    service = await anext(service_generator)
    await service_generator.aclose()

    assert isinstance(service.repository, PostgresSignalRepository)
    assert service.pipeline_executor.settings is settings
    assert service.pipeline_executor.public_data_client is public_data_client
    assert service.pipeline_executor.graph_provider is graph_provider
    assert context.entered is True
    assert context.exited is True
    clear_signal_graph_provider_cache()


class FakeRequest:
    def __init__(self, **state_values: object) -> None:
        self.app = FakeApp(**state_values)


class FakeApp:
    def __init__(self, **state_values: object) -> None:
        self.state = FakeState(**state_values)


class FakeState:
    def __init__(self, **values: object) -> None:
        for key, value in values.items():
            setattr(self, key, value)


class FakeSessionContext:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    def __call__(self) -> "FakeSessionContext":
        return self

    async def __aenter__(self) -> object:
        self.entered = True
        return object()

    async def __aexit__(self, *args: object) -> None:
        self.exited = True
