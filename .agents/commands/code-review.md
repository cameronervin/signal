Review current git changes using the code-review-expert skill.

Follow `.agents/skills/code-review-expert/SKILL.md`.

Signal-specific focus:
- FastAPI routes stay thin; orchestration belongs in services and persistence in repositories.
- DTO boundaries use Pydantic models, not raw dict contracts.
- Scores, tiers, gates, and drafts remain server-owned and explainable.
- Gate-failed leads must not expose drafts.
- Public API clients keep fixture/cache fallbacks.
- Frontend changes follow the SDR workspace design system in `backstage/design/README.md`.

Default prompt: Review for correctness, security, scoring/gate regressions, data leaks, race conditions, error handling, performance problems, and missing tests.
