import pytest

from app.agents.graph_provider import (
    clear_signal_graph_provider_cache,
    get_signal_graph_provider,
)
from app.api.v1.dependencies import (
    get_agent_execution_service,
    get_graph_provider_dependency,
    get_lead_intake_service,
    get_pipeline_executor,
    get_public_data_dependency,
    get_signal_repository,
)
from app.core.config import Settings
from app.infrastructure.public_data import create_public_data_client
from app.repositories.signal_snapshot import SignalSnapshotRepository


class FakeKnowledgeGraphService:
    async def close(self) -> None:
        return None


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
        knowledge_graph_service=FakeKnowledgeGraphService(),
    )

    repository_generator = get_signal_repository(request, settings)
    repository = await anext(repository_generator)
    executor = get_pipeline_executor(
        settings=settings,
        graph_provider=get_graph_provider_dependency(request),
        public_data_client=get_public_data_dependency(request, settings),
        knowledge_graph_service=request.app.state.knowledge_graph_service,
    )
    execution_service = get_agent_execution_service(repository, executor)
    service = get_lead_intake_service(repository, execution_service)
    await repository_generator.aclose()

    assert isinstance(service.repository, SignalSnapshotRepository)
    executor = service.agent_execution_service.pipeline_executor
    assert executor is not None
    assert executor.settings is settings
    assert executor.public_data_client is public_data_client
    assert executor.graph_provider is graph_provider
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

    def begin(self) -> "FakeSessionContext":
        return self

    def __call__(self) -> "FakeSessionContext":
        return self

    async def __aenter__(self) -> "FakeSessionContext":
        self.entered = True
        return self

    async def __aexit__(self, *args: object) -> None:
        self.exited = True

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None
