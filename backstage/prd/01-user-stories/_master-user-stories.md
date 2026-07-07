# Master User Stories

## Epic 1 - Lead Intake And Trigger

**US-1.1** As an SDR, I can submit a lead with contact, company, email, and
property location so the enrichment pipeline runs without manual research.

Acceptance:

- API accepts contact name, email, company, role, property address, city, state,
  and country.
- API returns an enriched lead record and an agent run id.
- Invalid inputs return clear validation errors.

**US-1.2** As an implementation owner, I can seed leads so the queue shows A,
B, and C tiers without live API dependencies.

Acceptance:

- Fixture data includes at least one gate-failed lead.
- Sample leads include draftable and non-draftable states.

## Epic 2 - Enrichment And Scoring

**US-2.1** As an SDR, I can see a score, tier, and why-line for each lead so I
know where to start.

Acceptance:

- Score is server-generated.
- Tier cutoffs are A >= 75, B 50-74, C < 50 or gate failed.
- Why-line names the top score drivers or failed gates.

**US-2.2** As an SDR, I can see flags for bad-fit or unverifiable leads so I do
not spend time on low-quality inbound.

Acceptance:

- Personal email domains are flagged.
- Failed gates suppress draft generation.
- Gate-failed detail view explains what failed.

## Epic 3 - Outreach Drafting

**US-3.1** As an SDR, I can review a draft email with cited facts so I can send
personalized outreach faster.

Acceptance:

- Draft includes subject and body.
- Draft cites source facts used for personalization.
- Draft is editable in the UI before send-like actions.

**US-3.2** As a sales manager, I can trust that outreach is human-reviewed before
delivery.

Acceptance:

- Agent runs stop at human review.
- Send-like UI actions are explicit and review-gated.

## Epic 4 - Agent Operations

**US-4.1** As an SDR manager, I can see current enrichment and outreach agent
runs so I know what is ready, running, or blocked.

Acceptance:

- Agent list shows run id, lead, stage, and status.
- Run detail shows pipeline steps and activity log.

## Epic 5 - Rollout Narrative

**US-5.1** As the presenter, I can explain how the MVP rolls out to a sales org.

Acceptance:

- Project plan covers shadow mode, pilot, metrics, stakeholders, and rollout.
- Success and kill criteria are documented.
