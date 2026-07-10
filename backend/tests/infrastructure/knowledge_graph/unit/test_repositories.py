import pytest

from app.infrastructure.knowledge_graph.repositories import (
    Neo4jKnowledgeGraphRepository,
)


@pytest.mark.asyncio
async def test_ingest_stores_edges_against_canonical_lead_node() -> None:
    tx = FakeTx()
    record = _record()

    await Neo4jKnowledgeGraphRepository._ingest_tx(
        tx,
        record,
        {
            "nodes": [
                {
                    "id": "lead:lead_current",
                    "kind": "lead",
                    "label": "Sample Contact",
                    "subtitle": "Current inbound lead",
                    "source_fact_ids": [],
                },
                {
                    "id": "contact:abc",
                    "kind": "contact",
                    "label": "Sample Contact",
                    "subtitle": "VP Leasing",
                    "source_fact_ids": [],
                },
            ],
            "edges": [
                {
                    "id": "lead:lead_current:HAS_CONTACT:contact:abc",
                    "source": "lead:lead_current",
                    "target": "contact:abc",
                    "relationship": "HAS_CONTACT",
                    "reason": "Lead input includes this contact.",
                    "confidence": 1.0,
                    "source_fact_ids": [],
                }
            ],
        },
    )

    node_ids = [params.get("id") for _, params in tx.calls if "id" in params]
    assert "lead:lead_current" not in node_ids
    assert "contact:abc" in node_ids

    relationship_params = tx.calls[-1][1]
    assert relationship_params["id"] == "lead_current:HAS_CONTACT:contact:abc"
    assert relationship_params["source"] == "lead_current"
    assert relationship_params["target"] == "contact:abc"


@pytest.mark.asyncio
async def test_find_related_leads_filters_to_canonical_lead_records() -> None:
    tx = FakeTx()

    await Neo4jKnowledgeGraphRepository._find_related_tx(tx, _record())

    query = tx.calls[0][0]
    assert "lead.company_normalized IS NOT NULL" in query


@pytest.mark.asyncio
async def test_delete_lead_graph_removes_legacy_projection_lead_node() -> None:
    tx = FakeTx()

    await Neo4jKnowledgeGraphRepository._delete_lead_tx(tx, "lead_current")

    query, params = tx.calls[0]
    assert "lead.id IN [$lead_id, $projection_lead_id]" in query
    assert params["lead_id"] == "lead_current"
    assert params["projection_lead_id"] == "lead:lead_current"


class FakeTx:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def run(self, query: str, **params: object):
        self.calls.append((query, params))
        return FakeResult()


class FakeResult:
    async def consume(self) -> None:
        return None

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


def _record() -> dict[str, object]:
    return {
        "lead_id": "lead_current",
        "label": "Sample Contact at Example Homes",
        "company_normalized": "example homes",
        "property_normalized": "100 main st austin tx",
        "market_normalized": "austin tx",
        "trigger_normalized": "portfolio expansion",
        "source_fact_ids": ["source_fact:abc"],
        "source_categories": ["news"],
    }
