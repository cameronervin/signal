# Security

Signal handles lead, enrichment, scoring, and draft outreach data. Treat it as
sensitive even when running as a take-home demo.

## Rules

- Validate inbound lead input with Pydantic.
- Keep CORS origins explicit.
- Store API keys and LLM credentials in environment variables only.
- Do not log full emails, raw request bodies, draft bodies, prompts, tokens,
  secrets, or raw provider payloads.
- Do not trust client-supplied score, tier, gate status, source facts, run
  state, or draft eligibility.
- Do not generate drafts for hard-gate-failed leads.
- Keep outbound behavior behind human review.
- V1 may copy/export reviewed draft text but must not send email.

## Data Minimization

V1 stores only:

- Lead input needed for enrichment and ranking.
- Normalized enrichment facts.
- Source facts used for scoring, talking points, and drafts.
- Gate results and flags.
- Score breakdown.
- Draft content only for gate-passed leads.
- Related-lead context.
- Agent run status, activity log, and degraded-provider notes.

Do not add new contact, resident, or account history fields without updating the
data model and explaining the sales workflow value.

## LLM Safety

- Pass only the minimum lead and source-fact context needed for scoring and
  drafting.
- Prompt the model to avoid unsupported claims.
- Require citations for personalization claims.
- Fall back to generic copy when source facts are insufficient.
- Do not log prompts, completions, draft bodies, or token payloads.

## Production Gaps

Before production use:

- Add auth and role-based access.
- Replace in-memory persistence with a durable database.
- Add audit logs for approve/copy/export and any future send action.
- Add provider timeout, retry, and rate-limit policies.
- Add retention policy for lead, enrichment, and draft data.
- Complete compliance review before live send or autonomous follow-up.
