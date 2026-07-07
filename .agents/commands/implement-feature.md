Implement a feature using the implement-feature skill.

Follow `.agents/skills/implement-feature/SKILL.md`.

Signal defaults:
- Read `backstage/prd/README.md`, `backstage/architecture/overview.md`, and the relevant technical spec before editing.
- Use TDD for non-trivial backend behavior, scoring changes, agent behavior, and frontend interactions with business rules.
- Keep runtime changes small, typed, and reviewable.
- Update docs when behavior changes.

Default prompt: Implement the requested Signal feature with focused tests first where appropriate, preserve demo-safe fallbacks and review gates, update docs, and verify with the relevant commands.
