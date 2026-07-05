---
name: github-issue-creator
description: Create GitHub issues and GitHub Project items from an approved implementation-plan phase. Use when the user asks to publish a PRD implementation plan, phase table, or agent-thread task list into GitHub issues for coding agents, including adding issues to a GitHub Project and writing issue URLs back to the plan after successful creation.
---

# GitHub Issue Creator

Use this skill to turn an aligned implementation-plan phase into GitHub issues,
with one issue per coding-agent thread. This skill performs live GitHub
mutations, so require explicit repo and project configuration before creating
anything.

## Preconditions

Proceed only when all are true:

- The user confirms the implementation plan phase is approved/aligned.
- A phase path is known.
- The repository is known as `OWNER/REPO` or `HOST/OWNER/REPO`.
- The GitHub Project owner and project number are known.
- GitHub auth has permission to create issues and edit projects.

If any required value is missing, ask for it. Do not guess from local remotes
when none exist. If a remote exists, present the discovered repo and ask only if
there is ambiguity.

Useful checks:

```bash
gh auth status
gh project view <PROJECT_NUMBER> --owner <PROJECT_OWNER> --format json
gh project field-list <PROJECT_NUMBER> --owner <PROJECT_OWNER> --format json
```

If project commands fail for auth scope, tell the user to run:

```bash
gh auth refresh -s project
```

## Phase 1: Read And Validate The Plan

Read exactly one approved phase file or one explicit phase section. Extract each
action row.

Each row must describe one coding-agent thread:

- One goal with one primary agent loop.
- Story/spec references.
- 3-5 acceptance criteria or an assertion-chain validation target.
- Likely touch points.
- Validation commands.
- Docs updates or `None`.
- Dependencies/blockers or `None`.
- Issue title, labels, milestone, assignees, or project field hints when present.

Reject or pause on rows that are too broad:

- Multiple unrelated workflows.
- Multiple independent agent loops.
- Missing acceptance criteria.
- Missing validation.
- Unresolved product decision.
- Requires live-send, paid dependency, auth/storage expansion, or other
  sensitive change without explicit approval.

When rejecting rows, report the row and how it should be split. Do not create
partial issue sets unless the user explicitly asks to publish only valid rows.

## Phase 2: Normalize Issue Content

For each valid row, create:

- Title: concise, imperative, and unique within the repo.
- Body with sections:
  - Summary.
  - Agent loop to use.
  - Story/spec references.
  - Acceptance criteria.
  - Likely touch points.
  - Validation commands.
  - Docs updates.
  - Dependencies/blockers.
  - Constraints and safety notes.
- Labels: from row metadata or sensible repo labels if discovered. Do not create
  new labels unless the user asks.
- Milestone and assignees only when explicitly configured.

Duplicate check before creating:

```bash
gh issue list -R <OWNER/REPO> --state all --search "<exact title>" --json number,title,url
```

If an open or closed issue clearly matches, ask whether to reuse, reopen, or
create a new issue. Do not silently duplicate.

## Phase 3: Create Issues And Project Items

Prefer explicit CLI commands because they are easy to audit.

Create the issue:

```bash
gh issue create \
  -R <OWNER/REPO> \
  --title "<TITLE>" \
  --body-file <BODY_FILE> \
  --label "<LABELS>" \
  --milestone "<MILESTONE>" \
  --assignee "<ASSIGNEES>"
```

Omit optional flags when values are absent.

Add it to the project:

```bash
gh project item-add <PROJECT_NUMBER> \
  --owner <PROJECT_OWNER> \
  --url <ISSUE_URL> \
  --format json
```

If the project has configured field mappings, set them after item creation:

```bash
gh project item-edit \
  --id <ITEM_ID> \
  --project-id <PROJECT_ID> \
  --field-id <FIELD_ID> \
  --single-select-option-id <OPTION_ID>
```

Use the GitHub MCP instead of `gh` only when the user requests it or the local
CLI is unavailable. Preserve the same validation and duplicate checks.

## Phase 4: Write Back Results

After each issue and project item succeeds:

- Add the issue URL to the row's `Issue` column or equivalent issue metadata.
- If the plan has no issue column, append a short `Published Issues` section
  mapping row goal to issue URL.
- Do not mark implementation status as done. Creating an issue is not
  implementation.

If issue creation succeeds but project add fails:

- Keep the issue URL.
- Report the project failure clearly.
- Ask whether to retry after auth/project config is fixed.
- Do not create duplicate replacement issues.

## Output Summary

Report:

- Number of issues created.
- Number of project items added.
- Any duplicates reused or skipped.
- Any rows rejected as oversized.
- Any plan file updated.
- Recovery commands for failures.

## Safety Rules

- Never create issues before the user confirms the phase is approved.
- Never infer trusted score, tier, send, auth, storage, or paid-dependency
  changes from vague plan text.
- Never include secrets, tokens, raw emails, or sensitive request bodies in issue
  titles or bodies.
- Never publish rows with unresolved product intent as implementation-ready.
