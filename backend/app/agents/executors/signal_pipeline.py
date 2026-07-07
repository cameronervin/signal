from typing import Any

from app.agents.graph_provider import SignalGraphProvider, get_signal_graph_provider
from app.agents.runtime_context import SignalRuntimeContext
from app.agents.states.signal_state import SignalState
from app.core.config import Settings, get_settings
from app.infrastructure.knowledge_graph import create_knowledge_graph_service
from app.infrastructure.public_data import PublicDataClient, get_public_data_client
from app.services.knowledge_graph_service import KnowledgeGraphService


class SignalPipelineExecutor:
    """Run the bounded Signal lead intelligence graph."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        checkpointer: Any | None = None,
        graph_provider: SignalGraphProvider | None = None,
        public_data_client: PublicDataClient | None = None,
        knowledge_graph_service: KnowledgeGraphService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.graph_provider = graph_provider or get_signal_graph_provider(
            settings=self.settings,
            checkpointer=checkpointer,
        )
        self.public_data_client = public_data_client or get_public_data_client(
            self.settings
        )
        self.knowledge_graph_service = (
            knowledge_graph_service or create_knowledge_graph_service(self.settings)
        )

    async def execute(self, initial_state: SignalState) -> SignalState:
        graph = self.graph_provider.signal_graph()
        result = await graph.ainvoke(
            initial_state,
            context=SignalRuntimeContext(
                settings=self.settings,
                public_data_client=self.public_data_client,
                knowledge_graph_service=self.knowledge_graph_service,
            ),
        )
        return result


async def run_signal_pipeline(initial_state: SignalState) -> SignalState:
    return await SignalPipelineExecutor().execute(initial_state)
