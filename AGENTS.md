# AGENTS.md - Signal Coding Instructions

Signal is an SDR-facing inbound lead intelligence tool for multifamily leasing
teams. It turns sparse inbound records into ranked, explained, outreach-ready
leads through a FastAPI and LangGraph backend plus a Next.js SDR workspace.

The product goal is simple: help a rep decide who to work first, what to say,
and how urgently to act.

## First Principles

1. **Read docs first** - Start with `backstage/prd/README.md`,
   `backstage/architecture/overview.md`, and the relevant technical spec.
2. **Keep Signal neutral** - Do not add third-party company or client brand
   names to code, copy, fixtures, prompts, docs, comments, tests, or env files.
3. **Prefer boring scaffolding** - Use clear FastAPI services, typed Pydantic
   contracts, Next.js App Router conventions, and LangGraph nodes with explicit
   state.
4. **Build in small slices** - Keep changes scoped, tested, and easy to review.
5. **Explain every score** - Scoring logic must stay config-driven,
   inspectable, and easy to recalibrate.
6. **Human review before outreach** - Draft and send flows must preserve a
   human-in-the-loop gate.
7. **Demo reliability matters** - Public API clients need cached or fixture
   fallbacks. Do not make the live demo depend on perfect external uptime.

## Architecture

```text
frontend/src/app/                 App Router routes
frontend/src/components/          UI primitives, layout, feature components
frontend/src/lib/                 API client, fixtures, constants, stores

backend/app/api/v1/               Thin FastAPI routers
backend/app/services/             Product orchestration
backend/app/repositories/         Persistence boundary
backend/app/agents/               LangGraph state, nodes, graph, prompts
backend/app/integrations/         Public API adapters and cache boundary
backend/app/schemas/              Pydantic request and response contracts
```

## Product Surface

| Surface | Purpose |
| --- | --- |
| Dashboard | Queue health, tier distribution, top markets, demo KPIs |
| Inbound leads | Ranked SDR queue sorted by tier and score |
| Lead detail | Enrichment, why-line, graph context, flags, cited draft |
| Agent assignment | Runs currently enriching, drafting, or awaiting review |
| Agent progress | Pipeline state, activity log, approval gate |
| Gate-failed lead | Clear no-draft state for leads reps should not work |

## Documentation Index

| Need | Read |
| --- | --- |
| MVP scope | `backstage/prd/README.md` |
| User stories | `backstage/prd/01-user-stories/_master-user-stories.md` |
| Data model | `backstage/prd/02-technical-docs/01-signal/data-model.md` |
| API contracts | `backstage/prd/02-technical-docs/01-signal/api-specification.md` |
| Agent pipeline | `backstage/prd/02-technical-docs/01-signal/agentic-framework.md` |
| Scoring | `backstage/prd/02-technical-docs/01-signal/scoring.md` |
| Public APIs | `backstage/prd/02-technical-docs/01-signal/integration-spec.md` |
| Design system | `backstage/design/README.md` |
| Setup | `backstage/guides/setup.md` |

## Working Rules

- Use TDD for non-trivial backend behavior, scoring changes, and frontend
  interactions with business rules.
- Keep FastAPI routes thin; put orchestration in services and persistence behind
  repositories.
- Use Pydantic models for request and response boundaries.
- Keep LangGraph state explicit and bounded; missing data should return flags,
  not hidden assumptions.
- Prefer Next.js App Router conventions and typed fixtures for demo fallback.
- Update docs after behavior changes, especially API, data model, scoring,
  integration, setup, and security docs.
- End each change with a summary of changed files, verification commands, docs
  updates, and open risks.

## Hard Boundaries

Always:

- Keep routes thin and business logic in services.
- Use structured DTOs instead of raw dict contracts.
- Add typed fixture adapters before live external API calls.
- Mask or omit raw emails and API keys in logs.
- Preserve the human review gate for outbound messaging.

Ask first:

- New persistent storage, auth, background worker, or live send behavior.
- New paid API dependency.
- Any change that alters scoring weights or tier thresholds.
- Any change that stores more lead/contact data than currently modeled.

Never:

- Add third-party brand names.
- Commit secrets or real API keys.
- Let client input set trusted score, tier, or gate-pass fields.
- Generate a draft for a hard-gate-failed lead.
- Log raw request bodies, draft text, secrets, tokens, or full emails.

## Verification

```bash
# Backend
cd backend && uv run pytest -v
cd backend && uv run ruff check .

# Frontend
cd frontend && pnpm test
cd frontend && pnpm lint
cd frontend && pnpm typecheck
```

If a command cannot run because dependencies are not installed, say that
plainly and include the install command.
