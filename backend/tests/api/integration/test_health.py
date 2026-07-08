from fastapi.testclient import TestClient

from app import main as api_main
from app.agents.graph_provider import SignalGraphProvider
from app.core.config import Settings
from app.infrastructure.public_data import PublicDataClient
from app.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "signal-api"}


def test_app_startup_does_not_create_database_schema() -> None:
    app = create_app(Settings(database_url="postgresql+asyncpg://invalid/unused"))

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_lifespan_warms_and_closes_app_duration_resources() -> None:
    app = create_app(Settings(database_url="postgresql+asyncpg://invalid/unused"))

    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        http_client = app.state.http_client

        assert response.status_code == 200
        assert app.state.sessionmaker is not None
        assert isinstance(app.state.public_data_client, PublicDataClient)
        assert app.state.public_data_client.http_client is http_client
        assert app.state.llm_provider.provider_name == "litellm"
        assert isinstance(app.state.signal_graph_provider, SignalGraphProvider)

    assert http_client.is_closed is True


def test_lifespan_initializes_and_shutdowns_langfuse(monkeypatch) -> None:
    calls: list[str] = []
    settings = Settings(database_url="postgresql+asyncpg://invalid/unused")
    app = create_app(settings)

    def fake_init_langfuse(app_settings: Settings) -> bool:
        assert app_settings is settings
        calls.append("init")
        return True

    def fake_verify(app_settings: Settings) -> dict[str, object]:
        assert app_settings is settings
        calls.append("verify")
        return {"enabled": True, "provider": "langfuse", "ready": True}

    monkeypatch.setattr(api_main, "init_langfuse", fake_init_langfuse)
    monkeypatch.setattr(api_main, "verify_tracing_configuration", fake_verify)
    monkeypatch.setattr(api_main, "shutdown_langfuse", lambda: calls.append("shutdown"))

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert calls[0:2] == ["init", "verify"]
    assert calls[-1] == "shutdown"
