import pytest

from app.core.config import Settings
from app.repositories.postgres import PostgresSignalRepository
from app.services import lead_service as lead_service_module
from app.services.lead_service import get_lead_service


@pytest.mark.asyncio
async def test_lead_service_dependency_uses_postgres_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(database_url="postgresql+asyncpg://postgres:test/db")
    context = FakeSessionContext()

    def fake_get_sessionmaker(settings_arg: Settings) -> FakeSessionContext:
        assert settings_arg is settings
        return context

    monkeypatch.setattr(
        lead_service_module,
        "get_sessionmaker",
        fake_get_sessionmaker,
    )

    service_generator = get_lead_service(settings)
    service = await anext(service_generator)
    await service_generator.aclose()

    assert isinstance(service.repository, PostgresSignalRepository)
    assert context.entered is True
    assert context.exited is True


class FakeSessionContext:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    def __call__(self) -> "FakeSessionContext":
        return self

    async def __aenter__(self) -> object:
        self.entered = True
        return object()

    async def __aexit__(self, *args: object) -> None:
        self.exited = True
