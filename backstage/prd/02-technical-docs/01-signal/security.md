# Security

Signal handles lead and outreach data. Treat it as sensitive even in a demo.

## Rules

- Validate all input with Pydantic.
- Keep CORS origins explicit.
- Store API keys in environment variables only.
- Do not log full emails, raw request bodies, draft bodies, prompts, tokens, or
  raw provider payloads.
- Do not trust client-supplied score, tier, gate status, or draft text.
- Do not generate drafts for hard-gate-failed leads.
- Keep outbound actions behind human review.

## Data Minimization

V1 stores only:

- Lead input.
- Normalized enrichment facts.
- Scoring breakdown.
- Flags.
- Draft if gates pass.
- Run status and activity log.

Do not add new contact enrichment fields without updating the data model and
explaining the sales workflow value.

## Production Gaps

Before production use:

- Add auth and role-based access.
- Replace in-memory persistence with a durable database.
- Add audit logs for approve/send actions.
- Expand provider retry policies beyond current bounded request timeouts and
  fixture fallback.
- Add retention policy for lead and draft data.
