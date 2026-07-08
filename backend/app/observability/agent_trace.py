"""Shared LangGraph invoke config for Signal tracing."""

from __future__ import annotations

import re
from typing import Any

from app.agents.states.signal_state import SignalState
from app.core.config import Settings, get_settings
from app.observability.langfuse_init import create_langfuse_handler, is_langfuse_ready

SIGNAL_TRACE_NAME = "signal.agent_run.execute"
SIGNAL_TRACE_MODE = "agent_run"
SIGNAL_TRACE_PHASE = "execute"

_SAFE_TRACE_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,199}$")


def verify_tracing_configuration(settings: Settings) -> dict[str, Any]:
    """Return a small startup-safe tracing readiness summary."""
    provider = "langfuse" if settings.langfuse_enabled else None
    return {
        "enabled": settings.tracing_enabled,
        "provider": provider,
        "ready": bool(
            settings.tracing_enabled
            and settings.langfuse_enabled
            and is_langfuse_ready()
        ),
    }


def build_signal_graph_invoke_config(
    initial_state: SignalState,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Build graph config with optional Langfuse callbacks and safe metadata."""
    app_settings = settings or get_settings()
    metadata = _build_safe_trace_metadata(initial_state, app_settings)
    config: dict[str, Any] = {
        "configurable": {
            "thread_id": metadata.get("run_id", initial_state["run_id"]),
            "run_id": initial_state["run_id"],
            "lead_id": initial_state["lead_id"],
            "mode": SIGNAL_TRACE_MODE,
            "phase": SIGNAL_TRACE_PHASE,
        },
        "run_name": SIGNAL_TRACE_NAME,
        "metadata": metadata,
        "tags": [
            "signal",
            f"env:{app_settings.env}",
            f"mode:{SIGNAL_TRACE_MODE}",
            f"phase:{SIGNAL_TRACE_PHASE}",
        ],
    }
    trigger = metadata.get("trigger")
    if trigger is not None:
        config["configurable"]["trigger"] = trigger

    callbacks = _build_trace_callbacks(app_settings)
    if callbacks:
        config["callbacks"] = callbacks

    return config


def _build_trace_callbacks(settings: Settings) -> list[Any]:
    if (
        not settings.tracing_enabled
        or not settings.langfuse_enabled
        or not is_langfuse_ready()
    ):
        return []

    handler = create_langfuse_handler()
    return [handler] if handler is not None else []


def _build_safe_trace_metadata(
    initial_state: SignalState,
    settings: Settings,
) -> dict[str, str]:
    values = {
        "environment": settings.env,
        "mode": SIGNAL_TRACE_MODE,
        "phase": SIGNAL_TRACE_PHASE,
        "run_id": initial_state["run_id"],
        "lead_id": initial_state["lead_id"],
        "trigger": _trigger_from_activity_log(initial_state.get("activity_log", [])),
        "langfuse_trace_name": SIGNAL_TRACE_NAME,
        "langfuse_session_id": initial_state["run_id"],
    }
    return {
        key: safe_value
        for key, value in values.items()
        if (safe_value := _safe_metadata_value(value)) is not None
    }


def _trigger_from_activity_log(activity_log: list[str]) -> str | None:
    if not activity_log:
        return None
    first_entry = activity_log[0]
    trigger, separator, _message = first_entry.partition(":")
    if not separator:
        return None
    return trigger.strip()


def _safe_metadata_value(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if _SAFE_TRACE_VALUE_RE.fullmatch(stripped):
        return stripped
    return None

