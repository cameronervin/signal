Debug a bug using the bug-squasher skill.

Follow `.agents/skills/bug-squasher/SKILL.md`.

Signal-specific defaults:
- Read `backstage/prd/README.md`, `backstage/architecture/overview.md`, and the relevant technical spec before proposing changes.
- Prefer hypothesis-driven debugging: list likely causes, verify with targeted evidence, then patch the smallest safe surface.
- Preserve demo reliability, fixture fallbacks, score explainability, no-draft hard gates, and the human review gate.
- Mask full emails, draft bodies, prompts, provider payloads, tokens, and API keys in logs and reports.

Default prompt: Debug the reported issue using hypothesis-driven analysis. Gather context, rank hypotheses, collect targeted evidence, identify root cause, apply a minimal fix, and verify with the relevant backend or frontend checks.
