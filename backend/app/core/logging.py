import logging
import re
from collections.abc import Mapping
from typing import Any

import structlog

EMAIL_RE = re.compile(
    r"(?P<first>[A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*"
    r"@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
)
SENSITIVE_KEY_PARTS = (
    "api_key",
    "authorization",
    "body",
    "completion",
    "draft",
    "email",
    "key",
    "password",
    "payload",
    "prompt",
    "request",
    "secret",
    "token",
)
REDACTED = "[redacted]"


def mask_email_text(value: str) -> str:
    return EMAIL_RE.sub(r"\g<first>***@\g<domain>", value)


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return mask_email_text(value)
    if isinstance(value, Mapping):
        return {
            key: REDACTED if is_sensitive_key(str(key)) else sanitize_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_value(item) for item in value)
    return value


def sanitize_log_event(
    logger: object,
    method_name: str | None,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    return {
        key: REDACTED if is_sensitive_key(str(key)) else sanitize_value(value)
        for key, value in event_dict.items()
    }


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level.upper(), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            sanitize_log_event,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )
