"""Langfuse initialization and masking for Signal agent traces."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from typing import Any

import structlog
from pydantic import BaseModel

from app.core.config import Settings, get_settings

logger = structlog.get_logger(__name__)

_initialized = False
_client: Any | None = None

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_SIGNED_URL_RE = re.compile(
    r"(?i)\bhttps?://(?=[^\s\"'<>)]*(?:x-amz-signature|"
    r"x-amz-security-token|signature)=)[^\s\"'<>),;]+"
)
_STORAGE_URI_RE = re.compile(r"(?i)\b(?:s3|gs)://[^\s\"'<>),;]+")
_SECRET_FRAGMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|authorization|bearer|password|secret|token)"
    r"([=:]\s*|\s+)[^\s\"'<>),;]+"
)
_REDACTION = "[redacted]"
_TRACE_SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "body",
    "draft",
    "draft_body",
    "draft_text",
    "email",
    "password",
    "secret",
    "signed_url",
    "source_uri",
    "storage_key",
    "subject",
    "token",
}
_TRACE_SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "password",
    "secret",
    "signature",
    "token",
)


def is_langfuse_ready() -> bool:
    """Return True when Langfuse has been initialized for this process."""
    return _initialized


def init_langfuse(settings: Settings | None = None) -> bool:
    """Initialize Langfuse lazily when tracing is enabled and configured."""
    global _client, _initialized
    app_settings = settings or get_settings()

    if not app_settings.langfuse_enabled:
        _reset_langfuse_state()
        logger.info("langfuse_tracing_disabled", langfuse_enabled=False)
        return False

    if not app_settings.langfuse_public_key or not app_settings.langfuse_secret_key:
        _reset_langfuse_state()
        logger.warning(
            "langfuse_credentials_missing",
            public_key_configured=bool(app_settings.langfuse_public_key),
            secret_key_configured=bool(app_settings.langfuse_secret_key),
        )
        return False

    try:
        from langfuse import Langfuse  # noqa: PLC0415
    except ImportError as exc:
        _reset_langfuse_state()
        logger.warning("langfuse_sdk_unavailable", error=str(exc))
        return False

    os.environ["LANGFUSE_PUBLIC_KEY"] = app_settings.langfuse_public_key
    os.environ["LANGFUSE_SECRET_KEY"] = app_settings.langfuse_secret_key
    os.environ["LANGFUSE_BASE_URL"] = app_settings.langfuse_base_url
    os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = app_settings.env

    try:
        _client = Langfuse(
            public_key=app_settings.langfuse_public_key,
            secret_key=app_settings.langfuse_secret_key,
            base_url=app_settings.langfuse_base_url,
            environment=app_settings.env,
            mask=mask_langfuse_data,
        )
    except Exception as exc:  # noqa: BLE001
        _reset_langfuse_state()
        logger.warning("langfuse_initialization_failed", error=str(exc))
        return False

    _initialized = True
    logger.info(
        "langfuse_tracing_initialized",
        base_url=app_settings.langfuse_base_url,
        environment=app_settings.env,
    )
    return True


def create_langfuse_handler() -> Any | None:
    """Create a fresh Langfuse LangChain callback handler for one graph run."""
    if not _initialized:
        return None

    try:
        from langfuse.langchain import CallbackHandler  # noqa: PLC0415
    except ImportError as exc:
        logger.warning("langfuse_callback_handler_unavailable", error=str(exc))
        return None

    return CallbackHandler()


def shutdown_langfuse() -> None:
    """Flush pending trace data and clear process-local Langfuse state."""
    global _client
    if not _initialized and _client is None:
        return

    try:
        if _client is not None:
            _client.shutdown()
        else:
            from langfuse import get_client  # noqa: PLC0415

            get_client().shutdown()
        logger.info("langfuse_client_shutdown")
    except Exception as exc:  # noqa: BLE001
        logger.warning("langfuse_shutdown_failed", error=str(exc))
    finally:
        _reset_langfuse_state()


def mask_langfuse_data(data: Any) -> Any:
    """Recursively mask sensitive trace fragments before export."""
    if isinstance(data, BaseModel):
        return mask_langfuse_data(data.model_dump(mode="json"))
    if isinstance(data, str):
        return _redact_trace_string(data)
    if isinstance(data, Mapping):
        return {
            key: _REDACTION
            if _is_trace_sensitive_key(key)
            else mask_langfuse_data(value)
            for key, value in data.items()
        }
    if isinstance(data, tuple):
        return tuple(mask_langfuse_data(item) for item in data)
    if isinstance(data, Sequence) and not isinstance(data, (bytes, bytearray)):
        return [mask_langfuse_data(item) for item in data]
    return data


def _reset_langfuse_state() -> None:
    global _client, _initialized
    _initialized = False
    _client = None


def _is_trace_sensitive_key(key: Any) -> bool:
    normalized = _normalize_key(key)
    return (
        normalized in _TRACE_SENSITIVE_KEYS
        or any(part in normalized for part in _TRACE_SENSITIVE_KEY_PARTS)
    )


def _normalize_key(key: Any) -> str:
    snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", str(key))
    return snake_case.lower().replace("-", "_").replace(" ", "_")


def _redact_trace_string(value: str) -> str:
    redacted = _SIGNED_URL_RE.sub(_REDACTION, value)
    redacted = _STORAGE_URI_RE.sub(_REDACTION, redacted)
    redacted = _EMAIL_RE.sub(_REDACTION, redacted)
    return _SECRET_FRAGMENT_RE.sub(r"\1\2[redacted]", redacted)

