# AGENTS.md - Signal Agent Harness

Signal is an internal SDR workspace for an AI leasing platform vendor. It helps
SDRs work inbound demo leads from multifamily operators by turning sparse lead
records into enriched, scored, explained, and outreach-ready opportunities.

The product goal is simple: help a rep decide who to work first, why the lead is
urgent, and what reviewed message to copy or export into existing sales tools.

## First Principles

1. **Read docs first** - Start with `backstage/prd/README.md`,
   `backstage/architecture/overview.md`, and the relevant technical spec.
2. **Keep Signal neutral** - Do not add source-company, competitor, client,
   prospect, or third-party company brand names to code, copy, fixtures,
   prompts, docs, comments, tests, or env files.
3. **Prefer boring scaffolding** - Use clear FastAPI services, typed Pydantic
   contracts, Next.js App Router conventions, and LangGraph nodes with explicit
   state.
4. **Use modern build loops** - Work from `.agents/loops/`; each loop has a
   goal, context pack, implementation pass, verification pass, and convergence
   criteria.
5. **Explain every score** - Scoring logic must stay config-driven,
   inspectable, and easy to recalibrate.
6. **Human review before outreach** - Draft, copy, export, and any future send
   flows must preserve a human-in-the-loop gate.
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
| Inbound lead trigger | Accept sparse demo leads and start enrichment |
| Ranked SDR queue | Sort leads by tier, score, and urgency |
| Lead detail | Show enrichment, score components, flags, related context, talking points, and cited draft |
| Draft review | Let SDRs review and copy/export outreach without sending |
| Agent runs | Show enrichment, LLM drafting, related-context, review, and degraded-provider states |
| Demo dashboard | Support seeded A/B/C, warning-only, and gate-failed walkthroughs |

## Documentation Index

| Need | Read |
| --- | --- |
| Product scope | `backstage/prd/README.md` |
| User stories | `backstage/prd/01-user-stories/_master-user-stories.md` |
| Data model | `backstage/prd/02-technical-docs/01-signal/data-model.md` |
| API contracts | `backstage/prd/02-technical-docs/01-signal/api-specification.md` |
| Agent pipeline | `backstage/prd/02-technical-docs/01-signal/agentic-framework.md` |
| Scoring | `backstage/prd/02-technical-docs/01-signal/scoring.md` |
| Public APIs | `backstage/prd/02-technical-docs/01-signal/integration-spec.md` |
| Evals | `backstage/prd/02-technical-docs/01-signal/eval-framework.md` |
| Security | `backstage/prd/02-technical-docs/01-signal/security.md` |
| Rollout | `backstage/prd/02-technical-docs/01-signal/rollout.md` |
| Implementation plan | `backstage/prd/03-implementation/_implementation-plan.md` |
| Design system | `backstage/design/README.md` |
| Setup | `backstage/guides/setup.md` |

## Rules - Read Before Editing

| Work type | Required rules |
| --- | --- |
| Any code change | `.agents/rules/00-tdd.md`, `.agents/rules/01-architecture.md`, `.agents/rules/05-security.md`, `.agents/rules/07-docs.md` |
| Backend Python | `.agents/rules/02-python.md`, `.agents/rules/04-agentic-pipeline.md` |
| Frontend TypeScript | `.agents/rules/03-frontend.md`, `.agents/style/design-tokens.md`, `.agents/style/ui-patterns.md` |
| Tests | `.agents/rules/06-testing.md` |
| Git work | `.agents/rules/08-git.md` |

## Loops

Modern agentic build loops live in `.agents/loops/`.

- `feature-build.loop.md` - normal product slices.
- `bugfix.loop.md` - hypothesis-driven debugging.
- `eval-calibration.loop.md` - scoring, prompt, fixture, and eval tuning.
- `frontend-fidelity.loop.md` - design-system implementation and visual QA.

Every loop should end with:

- Changed files summarized.
- Verification commands run.
- Docs updated or explicitly marked not needed.
- Open risks captured in `backstage/development/tech-debt-tracker.md`.

## Hard Boundaries

Always:

- Keep routes thin and business logic in services.
- Use structured DTOs instead of raw dict contracts.
- Add typed fixture adapters before live external API calls.
- Mask or omit raw emails and API keys in logs.
- Preserve the human review gate for draft, copy, export, and future send-like
  behavior.
- Keep source facts attached to score drivers and draft personalization claims.

Ask first:

- New persistent storage, auth, background worker, or live send behavior.
- New paid API dependency.
- Any change that alters scoring weights or tier thresholds.
- Any change that stores more lead/contact data than currently modeled.
- Replacing an existing PRD/spec set; ask whether to archive current docs under
  a versioned folder such as `backstage/prd/v1/` and create a fresh
  `backstage/prd/v2/`.

Never:

- Add source-company, competitor, client, prospect, or third-party company brand
  names.
- Commit secrets or real API keys.
- Let client input set trusted score, tier, gate-pass fields, or draft
  eligibility.
- Generate a draft for a hard-gate-failed lead.
- Send outreach from v1.
- Log raw request bodies, draft text, prompts, secrets, tokens, full emails, or
  raw provider payloads.

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
