from collections.abc import AsyncIterator

from fastapi import Depends, Request

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.agents.graph_provider import SignalGraphProvider
from app.core.config import Settings, get_request_settings
from app.infrastructure.db.session import get_sessionmaker
from app.infrastructure.knowledge_graph import create_knowledge_graph_service
from app.infrastructure.public_data import PublicDataClient, get_public_data_client
from app.repositories.signal_snapshot import SignalRepository, SignalSnapshotRepository
from app.services.agent_execution_service import AgentExecutionService
from app.services.agent_run_service import AgentRunService
from app.services.analytics_service import AnalyticsService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.lead_intake_service import LeadIntakeService


async def get_signal_repository(
    request: Request,
    settings: Settings = Depends(get_request_settings),
) -> AsyncIterator[SignalRepository]:
    session_factory = getattr(request.app.state, "sessionmaker", None)
    if session_factory is None:
        session_factory = get_sessionmaker(settings)

    context = (
        session_factory.begin()
        if hasattr(session_factory, "begin")
        else session_factory()
    )
    async with context as session:
        yield SignalSnapshotRepository(session)


def get_public_data_dependency(
    request: Request,
    settings: Settings = Depends(get_request_settings),
) -> PublicDataClient:
    public_data_client = getattr(request.app.state, "public_data_client", None)
    if public_data_client is not None:
        return public_data_client
    return get_public_data_client(settings)


def get_graph_provider_dependency(request: Request) -> SignalGraphProvider | None:
    return getattr(request.app.state, "signal_graph_provider", None)


async def get_knowledge_graph_dependency(
    request: Request,
    settings: Settings = Depends(get_request_settings),
) -> AsyncIterator[KnowledgeGraphService]:
    knowledge_graph_service = getattr(
        request.app.state,
        "knowledge_graph_service",
        None,
    )
    if knowledge_graph_service is not None:
        yield knowledge_graph_service
        return

    created_service = create_knowledge_graph_service(settings)
    try:
        yield created_service
    finally:
        await created_service.close()


def get_pipeline_executor(
    settings: Settings = Depends(get_request_settings),
    graph_provider: SignalGraphProvider | None = Depends(
        get_graph_provider_dependency
    ),
    public_data_client: PublicDataClient = Depends(get_public_data_dependency),
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_dependency
    ),
) -> SignalPipelineExecutor:
    return SignalPipelineExecutor(
        settings=settings,
        graph_provider=graph_provider,
        public_data_client=public_data_client,
        knowledge_graph_service=knowledge_graph_service,
    )


def get_agent_execution_service(
    repository: SignalRepository = Depends(get_signal_repository),
    pipeline_executor: SignalPipelineExecutor = Depends(get_pipeline_executor),
) -> AgentExecutionService:
    return AgentExecutionService(
        repository,
        pipeline_executor=pipeline_executor,
    )


def get_lead_intake_service(
    repository: SignalRepository = Depends(get_signal_repository),
    agent_execution_service: AgentExecutionService = Depends(
        get_agent_execution_service
    ),
) -> LeadIntakeService:
    return LeadIntakeService(
        repository,
        agent_execution_service=agent_execution_service,
    )


def get_agent_run_service(
    repository: SignalRepository = Depends(get_signal_repository),
) -> AgentRunService:
    return AgentRunService(repository)


def get_analytics_service(
    repository: SignalRepository = Depends(get_signal_repository),
) -> AnalyticsService:
    return AnalyticsService(repository)
