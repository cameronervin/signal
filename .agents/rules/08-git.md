# Git Rules

Use conventional commits when asked to commit:

```text
feat(scope): add lead intake endpoint
fix(scoring): suppress drafts for gate failures
docs(agents): add build loop guide
chore(scaffold): initialize workspace
```

Do:

- Keep commits atomic.
- Check `git status --short` before staging.
- Avoid staging unrelated user changes.
- Include tests/docs with the behavior change.

Do not:

- Force push without explicit instruction.
- Rewrite unrelated work.
- Commit secrets, local env files, or generated dependency directories.
