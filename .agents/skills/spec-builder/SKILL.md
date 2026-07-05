---
name: spec-builder
description: Build first-time or repo-adaptive product PRD/spec docs and implementation plans from no docs, partial docs, existing code, or product-owner interviews. Use when the user asks to create a PRD, product spec, technical spec set, user stories, implementation plan, or agent-ready issue plan without assuming a prior harness or documentation structure exists.
---

# Spec Builder

Use this skill to turn an unclear product idea, existing repo, partial notes,
or undocumented codebase into durable product specs and an implementation plan
that coding agents can execute one thread at a time.

Do not assume harness docs exist. Do not require V1 docs. Treat existing docs
as evidence, not as a prerequisite.

## Operating Rules

- Start by inspecting the repo before asking about anything discoverable.
- Speak plainly to the product owner. They may not be technical.
- Ask direct, useful questions until the product goal, users, workflows,
  constraints, non-goals, and success criteria are clear.
- Push back at most once per topic. If the product owner remains unsure, log:
  `[OWNER NOTE: Product owner unsure about {topic}. Recommended default: {recommendation}. Confirm before implementation.]`
- Do not mutate repo files during discovery unless the user has asked to
  generate the docs now.
- Prefer the repo's existing documentation and agent-loop conventions. Never
  archive, rename, or delete existing docs unless the user explicitly asks.

## Phase 1: Repo Discovery

Classify the repository before the interview:

| Mode | Evidence |
| --- | --- |
| `NO_DOCS` | No product docs, specs, user stories, or implementation plan found. |
| `PARTIAL_DOCS` | Some notes/specs exist, but no coherent PRD/spec/plan set. |
| `EXISTING_SPECS` | A coherent PRD/spec/implementation-plan structure exists. |
| `CODEBASE_ONLY` | Meaningful code exists, but product docs are absent or stale. |

Inspect, when present:

- Product docs: `backstage/prd/`, `prd/`, `docs/`, `README.md`.
- Agent loops and rules: `.agents/loops/`, `.agents/rules/`, `AGENTS.md`.
- Project shape: package files, routes, services, models, schemas, tests,
  design docs, API docs, and integration configs.
- GitHub/project config only as context. Do not create issues from this skill.

Choose the output root:

- If `backstage/prd/` exists, use `backstage/prd/`.
- Else if `prd/` exists, use `prd/`.
- Else if the repo has a clear docs convention, follow it.
- Else create `prd/`.

Checkpoint notes in a temporary planning area when helpful, such as
`.agents/plans/spec-builder-notes.md`. Remove temporary notes or clearly mark
them as draft before final handoff.

## Phase 2: Product Interview

Interview until these areas are decision-complete:

- Product mission: what the product does, for whom, and why now.
- Audience and roles: user types, admins, reviewers, operators, external users.
- Jobs-to-be-done: the concrete outcomes each role needs.
- Core workflows: step-by-step happy paths and review/approval gates.
- Data: objects, fields, relationships, retention, privacy sensitivity.
- Integrations: external systems, fallback behavior, uptime assumptions.
- AI/agent behavior: prompts, tools, approvals, citations, evals, and failure
  modes, if applicable.
- Business rules: permissions, gating, scoring, routing, notifications.
- UX expectations: screens, states, empty states, mobile/desktop needs.
- Edge cases: invalid input, missing data, duplicate records, retries,
  concurrency, and degraded external services.
- Security and compliance: auth, authorization, audit logs, secrets, PII.
- Success metrics: activation, completion, quality, time saved, reliability.
- Rollout: demo, pilot, migration, observability, support, and deadlines.
- Non-goals: what must stay out of scope for this version.

For each major decision, capture:

- Decision.
- Rationale.
- Source: repo evidence, user answer, or recommended default.
- Open risk or owner note, if any.

## Phase 3: Generate Specs

Generate only artifacts the product needs. Typical set:

- PRD landing page with product summary, users, goals, non-goals, and links.
- Master user stories, grouped by epic.
- Technical docs for data model, API, agent/AI flow, integrations, security,
  design/UX, rollout, and evaluation when relevant.
- Implementation plan with phase files.

For a repo with existing conventions, match them. For a fresh repo, use:

```text
prd/
  README.md
  01-user-stories/_master-user-stories.md
  02-technical-docs/
  03-implementation/_implementation-plan.md
  03-implementation/phase-1-<slug>.md
```

Technical specs must be concrete enough for implementation:

- Define interfaces, schemas, endpoints, state transitions, events, and errors
  where relevant.
- Identify source-of-truth boundaries and trusted vs untrusted fields.
- Include human-review gates for irreversible user-facing actions.
- Include fallback behavior for external dependencies.
- Mark unresolved areas with owner notes instead of silently guessing.

## Implementation Plan Contract

Every implementation-plan action row must be scoped to one coding-agent thread
using one agent loop.

Use the repo's existing loop names when present. If `.agents/loops/` exists,
each row must name the expected loop, such as `feature-build`, `bugfix`,
`frontend-fidelity`, or `eval-calibration`. If no loop system exists, name a
simple loop type: `feature`, `bugfix`, `docs`, `eval`, or `migration`.

Recommended phase table:

```markdown
| Status | Agent Loop | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Planned | feature-build | <one-thread goal> | US-01, api-spec.md | <3-5 testable bullets or assertion chain> | backend service, API route, UI view | <commands> | <docs to update> | <blocked by or none> | <title/labels or URL after created> |
```

Row-sizing rules:

- One row equals one coding-agent thread and one pull request-sized vertical
  slice.
- Split a row if it touches unrelated features, needs two agent loops, requires
  unresolved product decisions, or cannot be verified with a focused command set.
- Keep each row independently understandable: a future agent should not need
  surrounding prose to know what to build.
- Include validation that proves behavior, not vague activity.
- Include docs updates or explicitly say `None`.
- Include dependencies or explicitly say `None`.
- Keep status values stable: `Planned`, `In Progress`, `Blocked`, `Done`, or
  match the repo's existing status vocabulary.

Phase order should follow dependency and risk:

1. Foundations or hardening required for later work.
2. Core user workflows.
3. Integrations and AI/evaluation work.
4. UX polish and demo/readiness work.
5. Rollout, observability, and documentation.

## Phase 4: Alignment And Handoff

Before considering the plan final:

- Cross-check every user story appears in at least one implementation phase.
- Cross-check every plan row references existing or newly created specs.
- Confirm every row is one-thread-sized.
- Confirm acceptance criteria are testable.
- Confirm unresolved owner notes are visible.
- Ask the user to explicitly confirm the implementation plan is aligned.

After confirmation, say that the plan is ready for `$github-issue-creator`.
Do not create GitHub issues from this skill.

## Recovery

- If interrupted during discovery, re-run repo classification and continue from
  the latest notes or generated docs.
- If docs already exist, update or extend them in place unless the user asks for
  a fresh replacement.
- If product intent conflicts with code reality, document both and ask which
  should be treated as source of truth before writing implementation tasks.
