from app.core.config import Settings


def test_settings_reads_database_url_without_signal_prefix(
    monkeypatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db/signal")

    settings = Settings(_env_file=None)

    assert settings.database_url == "postgresql+asyncpg://user:pass@db/signal"


def test_settings_does_not_support_signal_database_url_alias(
    monkeypatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv(
        "SIGNAL_DATABASE_URL",
        "postgresql+asyncpg://wrong:wrong@db/wrong",
    )

    settings = Settings(_env_file=None)

    assert settings.database_url == (
        "postgresql+asyncpg://postgres:postgres@localhost:5433/signal"
    )


def test_settings_reads_signal_llm_model(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SIGNAL_LLM_MODEL", "signal-chat")

    settings = Settings(_env_file=None)

    assert settings.llm_model == "signal-chat"


def test_settings_reads_knowledge_graph_configuration(monkeypatch) -> None:
    monkeypatch.setenv("SIGNAL_KNOWLEDGE_GRAPH_ENABLED", "true")
    monkeypatch.setenv("SIGNAL_NEO4J_URI", "bolt://neo4j:7687")
    monkeypatch.setenv("SIGNAL_NEO4J_USER", "neo4j")
    monkeypatch.setenv("SIGNAL_NEO4J_PASSWORD", "local-password")
    monkeypatch.setenv("SIGNAL_NEO4J_DATABASE", "neo4j")

    settings = Settings(_env_file=None)

    assert settings.knowledge_graph_enabled is True
    assert settings.neo4j_uri == "bolt://neo4j:7687"
    assert settings.neo4j_user == "neo4j"
    assert settings.neo4j_password == "local-password"
    assert settings.neo4j_database == "neo4j"


def test_settings_reads_langfuse_tracing_configuration(monkeypatch) -> None:
    monkeypatch.setenv("TRACING_ENABLED", "true")
    monkeypatch.setenv("LANGFUSE_ENABLED", "true")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    monkeypatch.setenv("LANGFUSE_BASE_URL", "https://langfuse.test")

    settings = Settings(_env_file=None)

    assert settings.tracing_enabled is True
    assert settings.langfuse_enabled is True
    assert settings.langfuse_public_key == "pk-test"
    assert settings.langfuse_secret_key == "sk-test"
    assert settings.langfuse_base_url == "https://langfuse.test"
