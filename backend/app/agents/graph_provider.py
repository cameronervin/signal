from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agents.builders.graphs_builder import compile_signal_pipeline_graph
from app.core.config import Settings


@dataclass(frozen=True, slots=True)
class SignalGraphProviderKey:
    """Identity tuple for a process-local Signal graph provider."""

    settings_signature: str
    checkpointer_id: int | None

    @classmethod
    def from_dependencies(
        cls,
        *,
        settings: Settings,
        checkpointer: Any | None,
    ) -> SignalGraphProviderKey:
        return cls(
            settings_signature=settings.model_dump_json(),
            checkpointer_id=id(checkpointer) if checkpointer is not None else None,
        )


class SignalGraphProvider:
    """Lazily compile and reuse static Signal graphs for one process."""

    def __init__(
        self,
        *,
        settings: Settings,
        checkpointer: Any | None = None,
    ) -> None:
        self.settings = settings
        self.checkpointer = checkpointer
        self._signal_graph = None

    def signal_graph(self):
        """Return the cached compiled Signal lead pipeline graph."""
        if self._signal_graph is None:
            self._signal_graph = compile_signal_pipeline_graph(
                app_settings=self.settings,
                checkpointer=self.checkpointer,
            )
        return self._signal_graph


class SignalGraphProviderCache:
    """Process-local cache for a dependency-matched graph provider."""

    def __init__(self) -> None:
        self._provider: SignalGraphProvider | None = None
        self._key: SignalGraphProviderKey | None = None

    def get_or_create(
        self,
        *,
        settings: Settings,
        checkpointer: Any | None = None,
    ) -> SignalGraphProvider:
        key = SignalGraphProviderKey.from_dependencies(
            settings=settings,
            checkpointer=checkpointer,
        )
        if self._provider is None or self._key != key:
            self._provider = SignalGraphProvider(
                settings=settings,
                checkpointer=checkpointer,
            )
            self._key = key
        return self._provider

    def clear(self) -> None:
        self._provider = None
        self._key = None


_signal_graph_provider_cache = SignalGraphProviderCache()


def get_signal_graph_provider(
    *,
    settings: Settings,
    checkpointer: Any | None = None,
) -> SignalGraphProvider:
    return _signal_graph_provider_cache.get_or_create(
        settings=settings,
        checkpointer=checkpointer,
    )


def clear_signal_graph_provider_cache() -> None:
    _signal_graph_provider_cache.clear()
