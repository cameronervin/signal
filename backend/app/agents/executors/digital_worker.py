from uuid import UUID

from app.agents.context.digital_worker_lifecycle import (
    DigitalWorkerLifecycleSpec,
    load_default_lifecycle_spec,
)
from app.agents.graph_provider import SignalGraphProvider, get_signal_graph_provider
from app.agents.runtime_context import DigitalWorkerRuntimeContext
from app.agents.states.digital_worker_state import DigitalWorkerState
from app.core.config import Settings, get_settings
from app.repositories.digital_worker import DigitalWorkerRepository
from app.repositories.signal_snapshot import SignalRepository


class DigitalWorkerExecutor:
    """Run one bounded SDR Digital Worker graph wake-up."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        signal_repository: SignalRepository,
        worker_repository: DigitalWorkerRepository,
        lifecycle: DigitalWorkerLifecycleSpec | None = None,
        graph_provider: SignalGraphProvider | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.signal_repository = signal_repository
        self.worker_repository = worker_repository
        self.lifecycle = lifecycle or load_default_lifecycle_spec()
        self.graph_provider = graph_provider or get_signal_graph_provider(
            settings=self.settings
        )

    async def execute(self, run_id: UUID) -> DigitalWorkerState:
        graph = self.graph_provider.digital_worker_graph()
        return await graph.ainvoke(
            {"run_id": run_id},
            context=DigitalWorkerRuntimeContext(
                settings=self.settings,
                signal_repository=self.signal_repository,
                worker_repository=self.worker_repository,
                lifecycle=self.lifecycle,
            ),
        )
