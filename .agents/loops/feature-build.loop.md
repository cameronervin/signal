# Feature Build Loop

## Context Pack

Read:

- `AGENTS.md`
- Relevant user story in `backstage/prd/01-user-stories/_master-user-stories.md`
- Relevant technical spec in `backstage/prd/02-technical-docs/01-signal/`
- Applicable rules under `.agents/rules/`

## Loop

1. Define acceptance criteria in 3-5 bullets.
2. Identify affected layers and test files.
3. Write or update focused tests first for non-trivial behavior.
4. Implement the smallest vertical slice.
5. Run targeted tests.
6. Refactor only inside the touched slice.
7. Run broader verification if contracts changed.
8. Update docs.

## Convergence

Stop when acceptance criteria pass, docs reflect the behavior, and remaining
risks are captured.
