Create the next Signal implementation phase document.

## Steps

1. Read `backstage/prd/03-implementation/_implementation-plan.md` and every `phase-*.md` file.
2. Cross-reference `backstage/prd/01-user-stories/_master-user-stories.md` and relevant specs under `backstage/prd/02-technical-docs/01-signal/`.
3. Inspect the codebase to verify which planned goals are already complete.
4. Define the next narrow phase around demo-safe, reviewable slices.
5. Create a deliverables table with: Status | Work Type | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue.
6. Use the repo's existing phase file style and concrete validation commands.

## Output Path

Write to `backstage/prd/03-implementation/phase-{N}-{short-title}.md`.

## Validation Criteria Style

Use concrete action-result-verification language, for example:

```text
Create lead -> pipeline enriches and scores -> lead detail shows tier, why-line, flags, and review-gated draft.
```

Default prompt: Generate the next implementation phase by reconciling current code, existing phase docs, user stories, and technical specs.
