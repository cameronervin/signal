from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any

import pytest

from app.core.config import Settings
from app.observability import langfuse_init
from app.schemas.lead import DraftEmail


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {"env": "test"}
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.fixture(autouse=True)
def reset_langfuse_state(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    env_names = (
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_BASE_URL",
        "LANGFUSE_TRACING_ENVIRONMENT",
    )
    monkeypatch.setattr(langfuse_init, "_initialized", False)
    monkeypatch.setattr(langfuse_init, "_client", None, raising=False)
    for env_name in env_names:
        monkeypatch.delenv(env_name, raising=False)
    yield
    for env_name in env_names:
        os.environ.pop(env_name, None)


def test_init_langfuse_noops_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "langfuse", ModuleType("langfuse"))

    ready = langfuse_init.init_langfuse(
        _settings(
            langfuse_enabled=False,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test",
        )
    )

    assert ready is False
    assert langfuse_init.is_langfuse_ready() is False


def test_init_langfuse_requires_credentials() -> None:
    ready = langfuse_init.init_langfuse(
        _settings(
            langfuse_enabled=True,
            langfuse_public_key="",
            langfuse_secret_key="",
        )
    )

    assert ready is False
    assert langfuse_init.is_langfuse_ready() is False


def test_init_langfuse_creates_client_with_mask(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[dict[str, Any]] = []

    class FakeLangfuse:
        def __init__(self, **kwargs: Any) -> None:
            created.append(kwargs)

        def shutdown(self) -> None:
            return None

    fake_module = ModuleType("langfuse")
    fake_module.Langfuse = FakeLangfuse
    monkeypatch.setitem(sys.modules, "langfuse", fake_module)

    ready = langfuse_init.init_langfuse(
        _settings(
            langfuse_enabled=True,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test",
            langfuse_base_url="https://langfuse.test",
        )
    )

    assert ready is True
    assert langfuse_init.is_langfuse_ready() is True
    assert created == [
        {
            "public_key": "pk-test",
            "secret_key": "sk-test",
            "base_url": "https://langfuse.test",
            "environment": "test",
            "mask": langfuse_init.mask_langfuse_data,
        }
    ]


def test_create_langfuse_handler_returns_fresh_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLangfuse:
        def __init__(self, **_: Any) -> None:
            return None

    class FakeCallbackHandler:
        def __init__(self) -> None:
            return None

    fake_module = ModuleType("langfuse")
    fake_module.Langfuse = FakeLangfuse
    fake_langchain_module = ModuleType("langfuse.langchain")
    fake_langchain_module.CallbackHandler = FakeCallbackHandler
    monkeypatch.setitem(sys.modules, "langfuse", fake_module)
    monkeypatch.setitem(sys.modules, "langfuse.langchain", fake_langchain_module)

    langfuse_init.init_langfuse(
        _settings(
            langfuse_enabled=True,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test",
        )
    )

    first = langfuse_init.create_langfuse_handler()
    second = langfuse_init.create_langfuse_handler()

    assert isinstance(first, FakeCallbackHandler)
    assert isinstance(second, FakeCallbackHandler)
    assert first is not second


def test_mask_langfuse_data_redacts_sensitive_trace_fragments() -> None:
    payload = {
        "input": "Lead wrote from avery@example.test with token=abc123",
        "draft": DraftEmail(
            subject="Follow up",
            body="Private outreach copy",
            sources=[],
        ),
        "metadata": {
            "run_id": "run-123",
            "lead_id": "lead-456",
            "email": "avery@example.test",
            "signed_url": "https://storage.test/file.pdf?X-Amz-Signature=abc",
            "source_uri": "s3://private-bucket/source.pdf",
        },
    }

    masked = langfuse_init.mask_langfuse_data(payload)
    rendered = repr(masked)

    assert masked["input"] == "Lead wrote from [redacted] with token=[redacted]"
    assert masked["draft"] == "[redacted]"
    assert masked["metadata"]["run_id"] == "run-123"
    assert masked["metadata"]["lead_id"] == "lead-456"
    assert masked["metadata"]["email"] == "[redacted]"
    assert masked["metadata"]["signed_url"] == "[redacted]"
    assert masked["metadata"]["source_uri"] == "[redacted]"
    assert "avery@example.test" not in rendered
    assert "Private outreach copy" not in rendered


def test_shutdown_langfuse_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    shutdown_calls = 0

    class FakeLangfuse:
        def __init__(self, **_: Any) -> None:
            return None

        def shutdown(self) -> None:
            nonlocal shutdown_calls
            shutdown_calls += 1

    fake_module = ModuleType("langfuse")
    fake_module.Langfuse = FakeLangfuse
    monkeypatch.setitem(sys.modules, "langfuse", fake_module)

    langfuse_init.init_langfuse(
        _settings(
            langfuse_enabled=True,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test",
        )
    )

    langfuse_init.shutdown_langfuse()
    langfuse_init.shutdown_langfuse()

    assert shutdown_calls == 1
    assert langfuse_init.is_langfuse_ready() is False
