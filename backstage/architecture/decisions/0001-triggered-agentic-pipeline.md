# ADR 0001 - Triggered Agentic Pipeline

## Status

Accepted.

## Context

The assignment requires automation by schedule or trigger. Signal needs a demo
path that is easy to explain and close to a production CRM workflow.

## Decision

Use an API trigger: `POST /api/v1/leads` represents a new inbound lead inserted
from a form, sheet, or CRM workflow. The endpoint invokes the same enrichment
pipeline that a production webhook would call.

## Consequences

- Demo can show one lead being inserted and enriched immediately.
- Production CRM integration is a boundary change, not a pipeline rewrite.
- Scheduling can be added later for batch backfills but is not needed for v1.
