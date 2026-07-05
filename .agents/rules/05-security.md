# Security Rules

## Do

- Validate all inbound lead input.
- Keep CORS origins explicit.
- Store API keys only in environment variables.
- Mask emails in logs and UI telemetry.
- Cache public API responses without secrets.
- Treat draft outreach as sensitive text.

## Do Not

- Commit `.env` files.
- Log raw request bodies, drafts, prompts, tokens, or API keys.
- Use wildcard CORS outside throwaway local experiments.
- Trust client-supplied score, tier, gate status, or draft text as final.
- Expose stack traces in production responses.

## Data Minimization

Store only the data required to rank, explain, and work the lead. If a feature
needs additional contact or company data, document the reason in the data model
and security spec before implementation.
