import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.leads import list_leads
from app.core.config import Settings
from app.core.logging import sanitize_log_event
from app.main import create_app
from app.services.lead_service import get_lead_service


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "signal-api"}


@pytest.mark.asyncio
async def test_openapi_schema_remains_available() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/openapi.json")

        assert response.status_code == 200
        assert response.json()["info"]["title"] == "Signal API"


@pytest.mark.asyncio
async def test_configured_cors_origin_allows_preflight() -> None:
    settings = Settings(frontend_origin="http://localhost:3100")
    async with AsyncClient(
        transport=ASGITransport(app=create_app(settings=settings)),
        base_url="http://testserver",
    ) as client:
        response = await client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3100",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert (
            response.headers["access-control-allow-origin"]
            == "http://localhost:3100"
        )


@pytest.mark.asyncio
async def test_app_factory_accepts_dependency_overrides() -> None:
    class StubLeadService:
        async def list_leads(self) -> list[object]:
            return []

    app = create_app(lead_service=StubLeadService())
    assert get_lead_service in app.dependency_overrides
    override = app.dependency_overrides[get_lead_service]

    assert await list_leads(await override()) == []


def test_settings_cover_demo_safe_backend_configuration() -> None:
    settings = Settings()

    assert settings.use_fixtures is True
    assert settings.api_base_url == "http://127.0.0.1:8000"
    assert settings.frontend_origin == "http://localhost:3000"
    assert "http://localhost:3000" in settings.cors_origins
    assert settings.scoring_config_path
    assert settings.max_agent_retries >= 0
    assert settings.provider_timeout_seconds > 0
    assert settings.request_timeout_seconds > 0
    assert settings.agent_execution_mode == "inline"
    assert settings.celery_agent_queue == "signal-agent-runs"
    assert settings.enable_demo_seed_endpoint is False
    assert settings.has_llm_key is False

    assert Settings(openai_api_key="test-key").has_llm_key is True
    assert Settings(litellm_gateway_key="test-key").has_llm_key is True


def test_settings_parse_comma_separated_extra_cors_origins_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "SIGNAL_EXTRA_CORS_ORIGINS",
        "http://127.0.0.1:3000, http://localhost:3100",
    )

    settings = Settings()

    assert settings.extra_cors_origins == [
        "http://127.0.0.1:3000",
        "http://localhost:3100",
    ]
    assert "http://localhost:3100" in settings.cors_origins


def test_settings_treat_blank_optional_provider_env_values_as_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in (
        "SIGNAL_NEWS_API_KEY",
        "SIGNAL_FRED_API_KEY",
        "SIGNAL_OPENAI_API_KEY",
        "SIGNAL_LITELLM_GATEWAY_URL",
        "SIGNAL_LITELLM_GATEWAY_KEY",
        "SIGNAL_LLM_MODEL",
    ):
        monkeypatch.setenv(key, "")

    settings = Settings()

    assert settings.news_api_key is None
    assert settings.fred_api_key is None
    assert settings.openai_api_key is None
    assert settings.litellm_gateway_url is None
    assert settings.litellm_gateway_key is None
    assert settings.llm_model is None
    assert settings.has_llm_key is False


def test_structured_logging_sanitizes_sensitive_values() -> None:
    sanitized = sanitize_log_event(
        None,
        None,
        {
            "email": "contact@operator.example",
            "message": "received contact@operator.example",
            "request_body": {"safe": "value"},
            "nested": {
                "api_key": "secret-key",
                "token": "secret-token",
                "prompt": "draft a message",
            },
        },
    )

    assert sanitized["email"] == "[redacted]"
    assert sanitized["message"] == "received c***@operator.example"
    assert sanitized["request_body"] == "[redacted]"
    assert sanitized["nested"]["api_key"] == "[redacted]"
    assert sanitized["nested"]["token"] == "[redacted]"
    assert sanitized["nested"]["prompt"] == "[redacted]"
