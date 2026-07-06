# Bug Log

Track reproduced bugs here.

| Date | ID | Summary | Status | Notes |
| --- | --- | --- | --- | --- |
| 2026-07-05 | B-001 | Initial scaffold | Closed | No known product bugs yet |
| 2026-07-06 | B-002 | Comma-separated `SIGNAL_EXTRA_CORS_ORIGINS` failed settings startup parsing | Closed | Marked the list field with Pydantic Settings `NoDecode` and added env-backed regression coverage |
| 2026-07-06 | B-003 | Blank optional provider and LLM env values failed settings startup or key-presence checks | Closed | Normalized blank optional values to unset and added env-backed regression coverage |
| 2026-07-06 | B-004 | Unsupported fixture geocoding could resolve to default US coordinates | Closed | Restricted fixture geocoding to explicit city/state keys and added hard-gate draft-suppression plus live fallback regression coverage |
