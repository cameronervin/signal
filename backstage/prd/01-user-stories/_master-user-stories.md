# Master User Stories

## Epic 1 - Lead Intake And Demo Trigger

**US-1.1** As an SDR, I can submit an inbound demo lead with contact, company,
email, and property location so Signal can enrich and rank it without manual
research.

Acceptance:

- API accepts contact name, email, company, property address, city, state, and
  country.
- API returns an enriched lead record and agent run id.
- Invalid inputs return clear validation errors.
- Trigger semantics are documented as the production-compatible stand-in for a
  future CRM or form webhook.

**US-1.2** As a demo operator, I can seed leads so the queue reliably shows A,
B, C, and gate-failed outcomes without depending on live API uptime.

Acceptance:

- Seeded leads cover draftable and non-draftable states.
- At least one seeded lead fails a hard gate and has no draft body.
- Seeded data can be reset repeatedly with stable ids or stable lookup handles.

## Epic 2 - Enrichment And Evidence

**US-2.1** As an SDR, I can see enriched account, property, market, and trigger
facts so I understand why the lead may be valuable.

Acceptance:

- Enrichment includes normalized facts from geocoding, demographic/economic,
  local-context, news/event, company-context, and domain-quality sources when
  available.
- Every fact used in scoring or draft personalization is represented as a
  source fact.
- Provider failures degrade to cached/fixture facts, warnings, or clear no-data
  states.

**US-2.2** As an SDR, I can see lead-quality flags so I do not spend time on
unverified or bad-fit inbound leads.

Acceptance:

- Hard gates cover non-corporate or invalid email domain, unresolved company,
  and non-US or unresolved property address.
- Gate failures force C-tier and suppress draft generation.
- Warnings are visible but do not suppress drafts unless a hard gate fails.

## Epic 3 - Scoring And Prioritization

**US-3.1** As an SDR, I can see a score, tier, and why-line for every lead so I
know who to work first and how urgently to act.

Acceptance:

- Score, tier, and why-line are server-generated.
- Scoring uses documented gates, a 60-point company/contact fit rubric, a
  40-point market/property opportunity rubric, and bounded multipliers.
- Tiers are A >= 75, B 50-74, and C < 50 or gate-failed.
- Why-lines name the strongest score drivers or failed gates.

**US-3.2** As an SDR manager, I can inspect the score components so I can tune
the rubric after pilot feedback.

Acceptance:

- Score response includes component names, point values, and source facts where
  relevant.
- Rubric weights and thresholds are documented and intended to live in config.
- Calibration assumptions and future reweighting criteria are documented.

## Epic 4 - Outreach Preparation

**US-4.1** As an SDR, I can review a draft intro email with cited
personalization so I can move quickly while checking accuracy.

Acceptance:

- LLM-backed agent generates subject, body, talking points, and cited source
  references for gate-passed leads.
- Drafts fall back to a safe generic template only when LLM or citation context
  is unavailable.
- Drafts are absent for hard-gate-failed leads.
- SDR can copy or export reviewed draft content into existing sales tools.

**US-4.2** As an SDR manager, I can trust that Signal does not send outreach
automatically.

Acceptance:

- Send-like actions are review-gated.
- V1 supports copy/export only, not live send or autonomous follow-up.
- UI copy and API contracts make the review boundary explicit.

## Epic 5 - Related Context And Agent Operations

**US-5.1** As an SDR, I can see related-lead context so I know whether the
account, company, property, or market has shown repeat inbound activity.

Acceptance:

- Related context can link leads by company, parent/portfolio hint, market, or
  submarket.
- The v1 graph is lightweight and does not require a graph database.
- Related context appears on lead detail and can contribute a bounded scoring
  bonus when documented.

**US-5.2** As an SDR manager, I can see enrichment and drafting run status so I
know what is ready, running, degraded, or blocked.

Acceptance:

- Agent run list shows run id, lead, stage, status, and timestamp.
- Run detail shows deterministic enrichment, LLM scoring/drafting, graph build,
  review gate, and activity log.
- Degraded provider or LLM states are visible without exposing secrets,
  prompts, raw provider payloads, or raw draft logs.

## Epic 6 - Rollout And Demo Narrative

**US-6.1** As the presenter, I can explain how Signal satisfies the take-home
assignment and would roll out to a sales org.

Acceptance:

- Docs identify public APIs used and why.
- Docs explain enrichment, scoring, drafting, and output workflow.
- Rollout covers MVP testing, shadow mode, pilot, timelines, stakeholders,
  success criteria, and kill/rework criteria.
- Demo plan includes seeded A/B/C leads, one gate-failed lead, and cache/fixture
  fallback strategy.
