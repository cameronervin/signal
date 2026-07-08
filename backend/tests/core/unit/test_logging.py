import io
import logging

from app.core.logging import configure_logging, redact_log_message


def test_redact_log_message_masks_url_query_strings_and_sensitive_fragments() -> None:
    message = (
        "GET https://api.example.test/search?q=Austin&api_key=secret "
        "email=ops@example.test token=abc key=123 apiKey=456"
    )

    redacted = redact_log_message(message)

    assert redacted == (
        "GET https://api.example.test/search?[redacted] "
        "email=[redacted] token=[redacted] key=[redacted] apiKey=[redacted]"
    )
    assert "secret" not in redacted
    assert "ops@example.test" not in redacted


def test_configure_logging_redacts_stdlib_log_records() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    try:
        root.handlers = [handler]
        configure_logging("INFO")

        logging.getLogger("httpx").info(
            "HTTP Request: GET %s",
            "https://api.example.test/data?key=secret&email=ops@example.test",
        )

        output = stream.getvalue()
    finally:
        root.handlers = original_handlers
        root.setLevel(original_level)

    assert "https://api.example.test/data?[redacted]" in output
    assert "secret" not in output
    assert "ops@example.test" not in output
