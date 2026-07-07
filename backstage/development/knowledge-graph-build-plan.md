# Knowledge Graph Build Plan

## Summary

Build Signal's knowledge graph as a Neo4j-backed subsystem inside the existing
FastAPI backend. Postgres remains the source of truth for lead and run snapshots;
Neo4j stores relationship-native context that helps Signal explain why a lead is
related to a company, property, market, trigger, source fact, or previous lead.

The graph is written during the LangGraph lead pipeline, queried before scoring
and drafting, and projected back into `LeadResponse` for the React Flow lead
detail component. Keep the graph read-only in the UI and preserve the existing
human review and gate-failed no-draft behavior.

## Key Decisions

- Use Neo4j inside the backend boundary, not a separate microservice.
- Keep graph business logic in `backend/app/services/knowledge_graph_service.py`.
- Keep driver setup and Cypher in `backend/app/infrastructure/knowledge_graph/`.
- Pass the graph service through `SignalRuntimeContext`; do not capture request
  resources in the compiled LangGraph.
- Make Neo4j optional behind `SIGNAL_KNOWLEDGE_GRAPH_ENABLED`; disabled or
  unavailable graph storage returns explicit graph warnings and a current-lead
  graph projection.
- Preserve `related_leads` for backward compatibility while adding structured
  `knowledge_graph`.

## Implementation Order

1. **Add dependencies and configuration**
   - Add `neo4j` to backend dependencies.
   - Add settings:
     - `SIGNAL_KNOWLEDGE_GRAPH_ENABLED`
     - `SIGNAL_NEO4J_URI`
     - `SIGNAL_NEO4J_USER`
     - `SIGNAL_NEO4J_PASSWORD`
     - `SIGNAL_NEO4J_DATABASE`
  - Add Neo4j as its own optional Docker Compose service/container alongside
    Postgres, Valkey, and LiteLLM.
  - Publish the default local Neo4j ports for developer use:
    - `7474` for the Neo4j browser
    - `7687` for Bolt driver connections
  - Use host-facing backend defaults like `bolt://localhost:7687`; document that
    container-to-container connections should use `bolt://neo4j:7687`.
  - Update `.env.example`, deploy env examples, and local compose defaults for
    the Neo4j service.

2. **Create backend graph contracts**
   - Add `backend/app/schemas/knowledge_graph.py`.
   - Define graph node, edge, source, related-lead, graph-context, and
     lead-graph projection DTOs.
   - Extend `LeadResponse` with `knowledge_graph`.
   - Extend `SignalState` with `graph_context` and `knowledge_graph`.

3. **Create the knowledge graph service layer**
   - Add `backend/app/services/knowledge_graph_service.py`.
   - Implement deterministic entity normalization and graph node IDs.
   - Build current-lead graph projection from `LeadCreate` + `Enrichment`.
   - Implement relationship rules for related leads.
   - Keep this layer free of Neo4j driver code.

4. **Create the graph repository boundary**
   - Add a `KnowledgeGraphRepository` protocol with:
     - `ingest_lead_graph`
     - `find_related_leads`
     - `project_lead_graph` if projection needs store-backed data
     - `close`
   - Add a disabled/no-op repository for local and test fallback.
   - Add a Neo4j repository using idempotent `MERGE` writes and managed
     read/write transactions.

5. **Wire app and worker lifecycle**
   - Create one app-lifetime Neo4j async driver when graph storage is enabled.
   - Close the driver during FastAPI and worker shutdown.
   - Follow current Neo4j driver guidance: one top-level async driver, async
     sessions with context managers, and managed read/write transactions.

6. **Update the LangGraph pipeline**
   - Add `knowledge_graph_ingest` after deterministic enrichment.
   - Add `graph_context_retrieval` before deterministic scoring.
   - Keep `knowledge_graph_builder` as the final bounded projection step.
   - Use LangGraph runtime context for the graph service, matching current
     LangGraph guidance for per-run dependencies.

7. **Update scoring and drafting inputs**
   - Keep score weights and tier thresholds unchanged.
   - Allow retrieved graph context to contribute talking points and draft
     context only when source-backed and explainable.
   - Do not generate a draft for hard-gate-failed leads.

8. **Update API and frontend**
   - Add `knowledge_graph` to backend and TypeScript lead DTOs.
   - Update `KnowledgeGraph.tsx` to render backend-provided nodes and edges.
   - Keep React Flow read-only: `fitView`, no dragging, no connecting, no
     scroll-zoom.
   - Continue rendering `related_leads` so existing detail UI stays compatible.

9. **Update docs**
   - Update architecture, data model, API spec, agentic framework, setup, and
     security docs.
   - Note that Neo4j stores graph relationships, while Postgres remains the
     canonical lead/run snapshot store.

## Relationship Model

Build these core relationships:

- `Lead -> HAS_CONTACT -> Contact`
- `Contact -> WORKS_AT -> Company`
- `Lead -> ABOUT_PROPERTY -> Property`
- `Property -> IN_MARKET -> Market`
- `Lead -> HAS_SOURCE_FACT -> SourceFact`
- `Company -> HAS_TRIGGER -> Trigger`
- `Lead -> RELATED_TO -> Lead`

Related-lead rules:

- Same normalized company: high confidence.
- Same market plus similar company/property context: medium confidence.
- Shared trigger or source category: medium or low confidence.

Every returned edge must include `reason`, `confidence`, and any supporting
source facts. Never expose raw secrets, raw provider payloads, or full request
bodies in graph logs.

## Test Plan

Backend unit tests:

- Entity normalization and graph IDs are deterministic.
- Current-lead graph projection includes lead, contact, company, property,
  market, source fact, and trigger nodes when data exists.
- Same-company leads produce high-confidence `RELATED_TO` context.
- Same-market-only leads produce bounded medium-confidence context.
- Unrelated leads do not produce related edges.

Backend integration tests:

- Lead creation returns `knowledge_graph`.
- Gate-failed leads receive graph context but no draft.
- Disabled Neo4j mode returns a valid current-lead graph projection.
- Neo4j failures surface explicit graph warnings without hiding provider or
  model failures.

Frontend tests:

- Lead detail renders backend graph nodes and edges.
- Empty graph state renders gracefully.
- Existing related-leads list remains backward compatible.

Verification commands:

```bash
cd backend && uv run pytest -v
cd backend && uv run ruff check .
cd frontend && pnpm test
cd frontend && pnpm lint
cd frontend && pnpm typecheck
```

## Assumptions

- Neo4j is approved as a new persistent dependency.
- The first implementation remains in the existing backend process.
- No new public REST endpoint is required initially; `LeadResponse` carries the
  bounded graph projection.
- The graph may inform explanations and drafts, but client input still cannot
  set score, tier, gates, graph confidence, or draft state.
