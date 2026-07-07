# Security Rules

Signal handles lead and outreach data. Treat demo data as sensitive.

## Do

- Validate input with Pydantic.
- Keep CORS origins explicit.
- Store keys in environment variables only.
- Mask full emails in logs.
- Use parameterized SQLAlchemy queries.
- Keep outbound actions behind human review.
- Keep failed gates visible to users and suppress drafts for those leads.

## Do Not

- Log full emails, raw request bodies, draft bodies, prompts, tokens, API keys, or raw provider payloads.
- Commit secrets or real API keys.
- Trust client-side validation alone.
- Let client input set score, tier, gate-pass, or trusted run status fields.
- Add new stored contact/enrichment fields without updating data docs and explaining workflow value.

## Ask First

- Production auth or permissions.
- New persistent storage.
- New paid API dependency.
- Live send behavior.
