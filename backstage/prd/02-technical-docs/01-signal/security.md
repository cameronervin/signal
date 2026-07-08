# Security

Signal handles lead and outreach data. Treat it as sensitive in every
environment.

## Rules

- Validate all input with Pydantic.
- Keep CORS origins explicit.
- Store API keys in environment variables only.
- Do not log full emails, raw request bodies, draft bodies, prompts, tokens, or
  raw provider payloads.
- Do not trust client-supplied score, tier, gate status, or draft text.
- Do not trust client-supplied graph confidence, related-lead, or gate-pass
  fields.
- Do not generate drafts for hard-gate-failed leads.
- Keep outbound actions behind human review.
- Digital Worker email is sandbox-only until live-send safety, audit, auth, and
  compliance controls are explicitly added.
- Do not log Digital Worker message bodies, draft bodies, prompts, or full
  email addresses.

## Data Minimization

V1 stores only:

- Lead input.
- Normalized enrichment facts.
- Scoring breakdown.
- Flags.
- Bounded graph relationships and source-backed graph warnings.
- Draft if gates pass.
- Run status and activity log.
- Digital Worker assignment state, lifecycle goals, sandbox email messages, and
  scheduled follow-ups for assigned draft-ready leads.

Do not add new contact enrichment fields without updating the data model and
explaining the sales workflow value.

## Production Gaps

Before production use:

- Add auth and role-based access.
- Add production backup and restore procedures for Postgres.
- Add audit logs for approve/send actions.
- Expand provider retry policies beyond current bounded request timeouts and
  explicit provider warning states.
- Add retention policy for lead and draft data.
- Add live email/SMS provider controls, consent/unsubscribe handling, and
  production audit policy before enabling real communication delivery.
