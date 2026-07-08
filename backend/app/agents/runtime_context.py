from dataclasses import dataclass

from app.agents.context.digital_worker_lifecycle import DigitalWorkerLifecycleSpec
from app.core.config import Settings
from app.infrastructure.public_data import PublicDataClient
from app.repositories.digital_worker import DigitalWorkerRepository
from app.repositories.signal_snapshot import SignalRepository
from app.services.knowledge_graph_service import KnowledgeGraphService


@dataclass(frozen=True, slots=True)
class SignalRuntimeContext:
    settings: Settings
    public_data_client: PublicDataClient
    knowledge_graph_service: KnowledgeGraphService


@dataclass(frozen=True, slots=True)
class DigitalWorkerRuntimeContext:
    settings: Settings
    signal_repository: SignalRepository
    worker_repository: DigitalWorkerRepository
    lifecycle: DigitalWorkerLifecycleSpec
