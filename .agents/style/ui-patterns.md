# Signal UI Patterns

Use `backstage/design/README.md` as the visual source of truth.

## Primitive Strategy

- Build local primitives in `frontend/src/components/ui/`.
- Use `lucide-react` for icons.
- Keep cards for individual repeated items, modals, and framed tools.
- Avoid nesting cards inside cards.
- Keep dashboard and workspace surfaces dense, calm, and easy to scan.

## Screens

- Dashboard: queue health, tier distribution, top markets, and demo KPIs.
- Inbound leads: ranked queue sorted by tier and score, with filters and copy feedback.
- Lead detail: enrichment, flags, related context, cited draft, and human review actions.
- Agent assignment: current runs with stage and status.
- Agent progress: pipeline steps, activity log, approval gate.
- Gate-failed lead: explicit no-draft state with reasons.

## Behavior

- Server-owned values: score, tier, gates, run status, and draft availability.
- Demo fallback: typed fixtures stay available when APIs are missing or unavailable.
- Copy should be calm, plain-spoken, and sentence case.
- Gate failures must suppress draft actions.
- Send-like actions must preserve human review.
