from __future__ import annotations

from typing import Any

from neo4j import AsyncDriver

from app.schemas.knowledge_graph import (
    KnowledgeGraphLeadRecord,
    KnowledgeGraphRelatedCandidate,
    LeadKnowledgeGraph,
)
from app.services.knowledge_graph_service import KnowledgeGraphRepository


class DisabledKnowledgeGraphRepository:
    async def ingest_lead_graph(
        self,
        record: KnowledgeGraphLeadRecord,
        graph: LeadKnowledgeGraph,
    ) -> None:
        return None

    async def find_related_leads(
        self,
        record: KnowledgeGraphLeadRecord,
    ) -> list[KnowledgeGraphRelatedCandidate]:
        return []

    async def close(self) -> None:
        return None


class Neo4jKnowledgeGraphRepository:
    def __init__(
        self,
        *,
        driver: AsyncDriver,
        database: str | None,
    ) -> None:
        self.driver = driver
        self.database = database or None

    async def ingest_lead_graph(
        self,
        record: KnowledgeGraphLeadRecord,
        graph: LeadKnowledgeGraph,
    ) -> None:
        async with self.driver.session(database=self.database) as session:
            await session.execute_write(
                self._ingest_tx,
                record.model_dump(mode="json"),
                graph.model_dump(mode="json"),
            )

    async def find_related_leads(
        self,
        record: KnowledgeGraphLeadRecord,
    ) -> list[KnowledgeGraphRelatedCandidate]:
        async with self.driver.session(database=self.database) as session:
            records = await session.execute_read(
                self._find_related_tx,
                record.model_dump(mode="json"),
            )
        return [
            KnowledgeGraphRelatedCandidate.model_validate(candidate)
            for candidate in records
        ]

    async def close(self) -> None:
        await self.driver.close()

    @staticmethod
    async def _ingest_tx(
        tx: Any,
        record: dict[str, Any],
        graph: dict[str, Any],
    ) -> None:
        await _consume(
            tx.run(
                """
                MERGE (lead:Lead {id: $lead_id})
                SET lead.label = $label,
                    lead.company_normalized = $company_normalized,
                    lead.property_normalized = $property_normalized,
                    lead.market_normalized = $market_normalized,
                    lead.trigger_normalized = $trigger_normalized,
                    lead.source_fact_ids = $source_fact_ids,
                    lead.source_categories = $source_categories
                """,
                **record,
            )
        )
        for node in graph["nodes"]:
            label = _neo4j_label(node["kind"])
            await _consume(
                tx.run(
                    f"""
                    MERGE (entity:{label} {{id: $id}})
                    SET entity.kind = $kind,
                        entity.label = $label,
                        entity.subtitle = $subtitle,
                        entity.source_fact_ids = $source_fact_ids
                    """,
                    **node,
                )
            )
        for edge in graph["edges"]:
            relationship_type = _neo4j_relationship(edge["relationship"])
            await _consume(
                tx.run(
                    f"""
                    MATCH (source {{id: $source}})
                    MATCH (target {{id: $target}})
                    MERGE (source)-[relationship:{relationship_type} {{id: $id}}]
                        ->(target)
                    SET relationship.reason = $reason,
                        relationship.confidence = $confidence,
                        relationship.source_fact_ids = $source_fact_ids
                    """,
                    **edge,
                )
            )

    @staticmethod
    async def _find_related_tx(
        tx: Any,
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        result = await tx.run(
            """
            MATCH (lead:Lead)
            WHERE lead.id <> $lead_id
              AND (
                lead.company_normalized = $company_normalized
                OR lead.market_normalized = $market_normalized
                OR (
                  $trigger_normalized IS NOT NULL
                  AND lead.trigger_normalized = $trigger_normalized
                )
                OR any(
                  category IN coalesce(lead.source_categories, [])
                  WHERE category IN $source_categories
                )
              )
            RETURN lead.id AS lead_id,
                   lead.label AS label,
                   lead.company_normalized AS company_normalized,
                   lead.property_normalized AS property_normalized,
                   lead.market_normalized AS market_normalized,
                   lead.trigger_normalized AS trigger_normalized,
                   coalesce(lead.source_fact_ids, []) AS source_fact_ids,
                   coalesce(lead.source_categories, []) AS source_categories
            ORDER BY
              CASE WHEN lead.company_normalized = $company_normalized THEN 0
                   WHEN lead.market_normalized = $market_normalized THEN 1
                   ELSE 2
              END,
              lead.label
            LIMIT 20
            """,
            **record,
        )
        return [dict(row) async for row in result]


def as_knowledge_graph_repository(
    repository: KnowledgeGraphRepository,
) -> KnowledgeGraphRepository:
    return repository


async def _consume(result):
    await (await result).consume()


def _neo4j_label(kind: str) -> str:
    return {
        "lead": "Lead",
        "contact": "Contact",
        "company": "Company",
        "property": "Property",
        "market": "Market",
        "source_fact": "SourceFact",
        "trigger": "Trigger",
    }[kind]


def _neo4j_relationship(relationship: str) -> str:
    return {
        "HAS_CONTACT": "HAS_CONTACT",
        "WORKS_AT": "WORKS_AT",
        "ABOUT_PROPERTY": "ABOUT_PROPERTY",
        "IN_MARKET": "IN_MARKET",
        "HAS_SOURCE_FACT": "HAS_SOURCE_FACT",
        "HAS_TRIGGER": "HAS_TRIGGER",
        "RELATED_TO": "RELATED_TO",
    }[relationship]
