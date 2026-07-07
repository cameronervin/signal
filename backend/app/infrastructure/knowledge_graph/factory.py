from __future__ import annotations

from neo4j import AsyncGraphDatabase

from app.core.config import Settings
from app.infrastructure.knowledge_graph.repositories import (
    DisabledKnowledgeGraphRepository,
    Neo4jKnowledgeGraphRepository,
)
from app.services.knowledge_graph_service import KnowledgeGraphService


def create_knowledge_graph_service(settings: Settings) -> KnowledgeGraphService:
    if not settings.knowledge_graph_enabled:
        return KnowledgeGraphService(
            DisabledKnowledgeGraphRepository(),
            storage_enabled=False,
        )
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    return KnowledgeGraphService(
        Neo4jKnowledgeGraphRepository(
            driver=driver,
            database=settings.neo4j_database,
        ),
        storage_enabled=True,
    )
