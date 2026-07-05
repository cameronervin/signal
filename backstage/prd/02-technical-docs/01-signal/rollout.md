# Rollout

Signal v1 should roll out as a demo-safe, human-reviewed SDR decision-support
tool. It is not a system of record, does not send outreach, and does not replace
existing sales tools in v1.

## Assignment Deliverable Narrative

The take-home video should explain:

1. Which public APIs are used and why.
2. How the lead insertion trigger runs enrichment, scoring, drafting, and
   related-context building.
3. What assumptions drive the 60/40 scoring rubric.
4. How the queue, why-line, source facts, talking points, and cited draft help a
   sales rep act faster.
5. How the tool would be tested and rolled out in a sales org.

## Stages

| Stage | Timeline | Scope | Exit Criteria |
| --- | --- | --- | --- |
| MVP build and internal validation | Week 1 | Build trigger, enrichment, scoring, LLM draft, queue/detail, fixtures, and docs | Seeded demo shows A/B/C and gate-failed leads; score and draft assumptions are documented |
| Shadow mode | Weeks 2-3 | Run Signal against inbound leads without changing rep behavior | Baseline speed-to-lead, response rate, worked leads per rep, and meeting conversion are captured |
| Pilot | Weeks 4-7 | 3-5 SDRs use queue and reviewed draft copy/export | A-tier first-action time improves; why-line accuracy and draft usefulness meet targets |
| Graduated rollout | Weeks 8-10 | Expand by team or segment; pilot SDRs help enable peers | RevOps or GTM owner has runbook and calibration process |
| Calibration and next release | Quarter 2 | Regress score against conversion and rep feedback | Reweight rubric or scope follow-up automation with human approval |

## Stakeholders

| Stakeholder | Role |
| --- | --- |
| SDR manager | Process owner, score-quality reviewer, pilot sponsor |
| SDRs | Daily users and feedback source |
| RevOps or Sales Ops | Future owner of routing, CRM boundaries, and reporting |
| Marketing Ops | Lead-source and form-context partner |
| Sales leadership | Success-metric sponsor |
| Legal/Security | Review external API, LLM, data retention, and future send behavior |

## Success Criteria

- A-tier speed-to-first-action improves by 50% during pilot.
- SDRs can identify the top lead in under 30 seconds from the queue.
- SDR manager rates why-line accuracy above 80% on reviewed pilot leads.
- Drafts are copied/exported with minimal edits.
- Hard-gate-failed leads never show a draft body or send-like action.
- Demo can run from seeded data without live provider uptime.

## Kill Or Rework Criteria

- Scores are inversely correlated with SDR manager judgment.
- Drafts contain unsupported or hallucinated personalization.
- Enrichment latency breaks the speed-to-lead goal.
- Provider failures regularly block the queue.
- SDRs do not trust the why-line or score component explanation.

## Demo Plan

- Pre-seed a lead list with A, B, C, warning-only, and gate-failed outcomes.
- Show lead insertion or fixture reset.
- Show the agent run progressing through enrichment, LLM scoring/drafting,
  related context, and review gate.
- Open the ranked queue and explain tier ordering.
- Open a lead detail page and show score components, source facts, talking
  points, related context, and cited draft.
- Copy/export a reviewed draft.
- Open a gate-failed lead and show clear no-draft state.
- Show scoring config or spec to prove assumptions are documented and
  recalibratable.

## Open Owner Notes

[OWNER NOTE: Product owner input needed on pilot duration if this moves beyond
the take-home demo. Recommended default: two weeks of shadow mode followed by a
four-week pilot. Confirm before production implementation.]

[OWNER NOTE: Product owner input needed on production retention. Recommended
default: retain demo and pilot lead records for 90 days, then delete or
anonymize. Confirm before production implementation.]
