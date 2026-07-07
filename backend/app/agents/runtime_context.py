from dataclasses import dataclass

from app.core.config import Settings
from app.infrastructure.public_data import PublicDataClient
from app.services.knowledge_graph_service import KnowledgeGraphService


@dataclass(frozen=True, slots=True)
class SignalRuntimeContext:
    settings: Settings
    public_data_client: PublicDataClient
    knowledge_graph_service: KnowledgeGraphService
