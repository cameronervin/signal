# Rollout

Signal v1 should roll out as a production-oriented, human-reviewed decision
support tool.
The MVP is not a system of record and must not send outreach automatically.

## Audiences

| Role | Need |
| --- | --- |
| SDR | Know which inbound lead to work first and why |
| SDR manager | Trust the score, draft safety, and review status |
| Implementation owner | Reset and review a reliable A/B/C local evaluation queue |
| Implementation owner | Track pilot quality, risks, and next hardening work |

## Stages

| Stage | Scope | Entry Criteria | Exit Criteria |
| --- | --- | --- | --- |
| Local evaluation | Seeded sample-data walkthrough for product review | Seeded leads cover A, B, C, and gate-failed states | Queue, detail, run status, and gate-failed views can be reviewed repeatably |
| Shadow | Reps compare Signal ranking against current manual triage | Public-data adapters and LiteLLM are configured | Manager confirms score explanations are clear enough for pilot use |
| Pilot | A small team reviews drafts and manually sends from their existing tools | Human review gate is implemented and visible | Meeting conversion, response quality, and false positive notes are reviewed |
| Hardening | Production-readiness work outside v1 scope | Pilot shows enough value to continue | Auth, durable storage, audit logs, and retention policy are specified |

## Success Metrics

| Metric | Target For V1 |
| --- | --- |
| Queue usefulness | Reps can identify the top lead in under 30 seconds during review |
| Explanation quality | Every A/B lead has a why-line tied to score components |
| Draft safety | Gate-failed leads never expose a draft body or send-like action |
| Citation quality | Draft personalization claims map to `SourceFact` records |
| Operational reliability | Provider failures surface as warnings or no-draft states |

## Kill Or Recalibration Criteria

- A-tier leads do not outperform B/C leads during pilot review.
- Reps cannot explain why a lead received its tier after reading the why-line.
- Public API failures frequently remove enough context to block triage.
- Draft citations cannot support personalization claims.
- Review-gated send-like actions are ambiguous or easy to bypass.

## Operating Notes

- Keep outbound messaging behind explicit human review.
- Treat lead and draft data as sensitive in every environment.
- Surface provider failures explicitly; do not substitute production facts with
  sample data.
- Seed local sample records with `cd backend && uv run alembic upgrade head && uv run python scripts/seed_demo_leads.py`.
- Log score components and gate reasons, not full emails, raw request bodies,
  raw drafts, prompts, provider payloads, tokens, or secrets.

## Open Owner Notes

[OWNER NOTE: Product owner input needed on pilot duration. Recommended default:
two weeks of shadow mode followed by a four-week pilot. Confirm before
implementation.]

[OWNER NOTE: Product owner input needed on production retention. Recommended
default: retain local-evaluation and pilot lead records for 90 days, then delete or
anonymize. Confirm before implementation.]
