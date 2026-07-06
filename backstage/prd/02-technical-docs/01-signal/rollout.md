# Rollout

Signal v1 should roll out as a demo-safe, human-reviewed decision support tool.
The MVP is not a system of record and must not send outreach automatically.

## Audiences

| Role | Need |
| --- | --- |
| SDR | Know which inbound lead to work first and why |
| SDR manager | Trust the score, draft safety, and review status |
| Demo operator | Reset and present a reliable A/B/C lead queue |
| Implementation owner | Track pilot quality, risks, and next hardening work |

## Stages

| Stage | Scope | Entry Criteria | Exit Criteria |
| --- | --- | --- | --- |
| Demo | Fixture-backed walkthrough for the take-home narrative | Seeded leads cover A, B, C, and gate-failed states | Queue, detail, run status, and gate-failed views can be shown without live API uptime |
| Shadow | Reps compare Signal ranking against current manual triage | Live or cached adapters are enabled behind fallbacks | Manager confirms score explanations are clear enough for pilot use |
| Pilot | A small team reviews drafts and manually sends from their existing tools | Human review gate is implemented and visible | Meeting conversion, response quality, and false positive notes are reviewed |
| Hardening | Production-readiness work outside v1 scope | Pilot shows enough value to continue | Auth, durable storage, audit logs, and retention policy are specified |

## Success Metrics

| Metric | Target For V1 |
| --- | --- |
| Queue usefulness | Reps can identify the top lead in under 30 seconds during demo review |
| Explanation quality | Every A/B lead has a why-line tied to score components |
| Draft safety | Gate-failed leads never expose a draft body or send-like action |
| Citation quality | Draft personalization claims map to `SourceFact` records |
| Demo reliability | Seeded data works without live public API dependencies |

## Kill Or Recalibration Criteria

- A-tier leads do not outperform B/C leads during pilot review.
- Reps cannot explain why a lead received its tier after reading the why-line.
- Public API failures frequently remove enough context to block triage.
- Draft citations cannot support personalization claims.
- Review-gated send-like actions are ambiguous or easy to bypass.

## Operating Notes

- Keep outbound messaging behind explicit human review.
- Treat lead and draft data as sensitive even in demo environments.
- Use cached or fixture-backed enrichment whenever live providers fail.
- Log score components and gate reasons, not full emails, raw request bodies,
  raw drafts, prompts, provider payloads, tokens, or secrets.

## Open Owner Notes

[OWNER NOTE: Product owner input needed on pilot duration. Recommended default:
two weeks of shadow mode followed by a four-week pilot. Confirm before
implementation.]

[OWNER NOTE: Product owner input needed on production retention. Recommended
default: retain demo and pilot lead records for 90 days, then delete or
anonymize. Confirm before implementation.]
