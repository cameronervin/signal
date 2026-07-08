import logging
import re
from urllib.parse import urlsplit, urlunsplit

import structlog

URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+")
SENSITIVE_FRAGMENT_PATTERN = re.compile(
    r"(?i)\b(key|api_key|apiKey|token|email)=([^&\s\"'<>]+)"
)


class RedactingLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record.msg = redact_log_message(message)
        record.args = ()
        return True


def redact_log_message(message: object) -> str:
    redacted = URL_PATTERN.sub(_redact_url_match, str(message))
    return SENSITIVE_FRAGMENT_PATTERN.sub(r"\1=[redacted]", redacted)


def _redact_url_match(match: re.Match[str]) -> str:
    raw_url = match.group(0)
    trailing = ""
    while raw_url and raw_url[-1] in ".,;:":
        trailing = raw_url[-1] + trailing
        raw_url = raw_url[:-1]

    parsed = urlsplit(raw_url)
    if not parsed.query:
        return f"{raw_url}{trailing}"
    safe_url = urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, "[redacted]", parsed.fragment)
    )
    return f"{safe_url}{trailing}"


def _add_filter_once(target: logging.Logger | logging.Handler) -> None:
    if not any(isinstance(item, RedactingLogFilter) for item in target.filters):
        target.addFilter(RedactingLogFilter())


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level.upper(), format="%(message)s")
    root = logging.getLogger()
    root.setLevel(level.upper())
    _add_filter_once(root)
    for handler in root.handlers:
        _add_filter_once(handler)
    for logger_name in ("httpx", "httpcore", "litellm", "LiteLLM"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(level.upper())
        _add_filter_once(logger)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _redact_structlog_event,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )


def _redact_structlog_event(
    _logger: object,
    _method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
    return {key: _redact_value(value) for key, value in event_dict.items()}


def _redact_value(value: object) -> object:
    if isinstance(value, str):
        return redact_log_message(value)
    if isinstance(value, dict):
        return {key: _redact_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in value)
    return value
