Run a cleanup scan using the garbage-cleanup skill.

Follow `.agents/skills/garbage-cleanup/SKILL.md`.

Signal cleanup priorities:
- Dead code, unused imports, stale fixtures, and duplicate helpers.
- Layer drift across routes, services, repositories, agents, public-data adapters, and frontend components.
- Hardcoded score weights, tier thresholds, provider assumptions, or design values that should live in config/tokens.
- Unsafe logging or demo paths that expose full emails, drafts, prompts, provider payloads, tokens, or API keys.

Default prompt: Scan the codebase for dead code, stale scaffolding, repeated logic, and architectural drift. Report safe removals separately from changes that need a plan.
