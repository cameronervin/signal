from uuid import uuid4

from app.core.config import Settings
from app.observability import agent_trace


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {"env": "test"}
    values.update(overrides)
    return Settings(_env_file=None, **values)


def _state() -> dict[str, object]:
    return {
        "lead_id": str(uuid4()),
        "run_id": str(uuid4()),
        "lead": object(),
        "activity_log": ["api_insert: lead received"],
    }


def test_verify_tracing_configuration_reports_disabled_when_tracing_off(
    monkeypatch,
) -> None:
    monkeypatch.setattr(agent_trace, "is_langfuse_ready", lambda: True)

    status = agent_trace.verify_tracing_configuration(
        _settings(tracing_enabled=False, langfuse_enabled=True)
    )

    assert status == {
        "enabled": False,
        "provider": "langfuse",
        "ready": False,
    }


def test_build_signal_graph_invoke_config_omits_callbacks_when_tracing_disabled(
    monkeypatch,
) -> None:
    monkeypatch.setattr(agent_trace, "is_langfuse_ready", lambda: True)
    monkeypatch.setattr(agent_trace, "create_langfuse_handler", object)

    config = agent_trace.build_signal_graph_invoke_config(
        _state(),
        _settings(tracing_enabled=False, langfuse_enabled=True),
    )

    assert "callbacks" not in config


def test_build_signal_graph_invoke_config_omits_callbacks_without_ready_langfuse(
    monkeypatch,
) -> None:
    monkeypatch.setattr(agent_trace, "is_langfuse_ready", lambda: False)
    monkeypatch.setattr(agent_trace, "create_langfuse_handler", object)

    config = agent_trace.build_signal_graph_invoke_config(
        _state(),
        _settings(tracing_enabled=True, langfuse_enabled=True),
    )

    assert "callbacks" not in config


def test_build_signal_graph_invoke_config_attaches_fresh_langfuse_callback(
    monkeypatch,
) -> None:
    created: list[object] = []

    def fake_create_handler() -> object:
        handler = object()
        created.append(handler)
        return handler

    monkeypatch.setattr(agent_trace, "is_langfuse_ready", lambda: True)
    monkeypatch.setattr(agent_trace, "create_langfuse_handler", fake_create_handler)
    settings = _settings(tracing_enabled=True, langfuse_enabled=True)

    first = agent_trace.build_signal_graph_invoke_config(_state(), settings)
    second = agent_trace.build_signal_graph_invoke_config(_state(), settings)

    assert first["callbacks"] == [created[0]]
    assert second["callbacks"] == [created[1]]
    assert first["callbacks"][0] is not second["callbacks"][0]


def test_build_signal_graph_invoke_config_attaches_safe_metadata_only(
    monkeypatch,
) -> None:
    handler = object()
    state = _state()
    monkeypatch.setattr(agent_trace, "is_langfuse_ready", lambda: True)
    monkeypatch.setattr(agent_trace, "create_langfuse_handler", lambda: handler)

    config = agent_trace.build_signal_graph_invoke_config(
        state,
        _settings(tracing_enabled=True, langfuse_enabled=True),
    )

    assert config["callbacks"] == [handler]
    assert config["run_name"] == "signal.agent_run.execute"
    assert config["metadata"] == {
        "environment": "test",
        "mode": "agent_run",
        "phase": "execute",
        "run_id": state["run_id"],
        "lead_id": state["lead_id"],
        "trigger": "api_insert",
        "langfuse_trace_name": "signal.agent_run.execute",
        "langfuse_session_id": state["run_id"],
    }
    assert config["tags"] == [
        "signal",
        "env:test",
        "mode:agent_run",
        "phase:execute",
    ]
    assert "lead" not in config["metadata"]
    assert "email" not in config["metadata"]
