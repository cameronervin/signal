# Bug Log

Track reproduced bugs here.

| Date | ID | Summary | Status | Notes |
| --- | --- | --- | --- | --- |
| 2026-07-05 | B-001 | Initial scaffold | Closed | No known product bugs yet |
| 2026-07-06 | B-002 | Comma-separated `SIGNAL_EXTRA_CORS_ORIGINS` failed settings startup parsing | Closed | Marked the list field with Pydantic Settings `NoDecode` and added env-backed regression coverage |
| 2026-07-06 | B-003 | Blank optional provider and LLM env values failed settings startup or key-presence checks | Closed | Normalized blank optional values to unset and added env-backed regression coverage |
| 2026-07-06 | B-004 | Unsupported fixture geocoding could resolve to default US coordinates | Closed | Restricted fixture geocoding to explicit fixture keys and added hard-gate draft-suppression plus live fallback regression coverage |
| 2026-07-06 | B-005 | Fixture geocoding and negative DNS fallbacks could allow unsupported leads through hard gates | Closed | Required explicit street/city/state fixture geocoding keys, treated negative MX answers as invalid or unknown, and added adapter plus pipeline regression coverage |
| 2026-07-06 | B-006 | Seed reset endpoint was mounted by default | Closed | Added explicit `SIGNAL_ENABLE_DEMO_SEED_ENDPOINT` route mounting and regression coverage |
| 2026-07-06 | B-007 | Client-supplied lead source could claim seeded related-context scoring | Closed | Added server-trigger graph state, blocked API-inserted leads from seeded related context, and aligned fixture source labels with scoring refs |
| 2026-07-06 | B-008 | Example scoring config path pointed at Python while scorer expected JSON | Closed | Updated `.env.example` to the versioned JSON rubric path and added regression coverage that the example path loads |
