from fastapi.testclient import TestClient

from app.core.config import Settings
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
