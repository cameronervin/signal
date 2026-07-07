Create a git commit using conventional commit style.

## Format

```text
<type>(<scope>): <subject>

<body>
```

## Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting/style-only change
- `refactor`: Code restructuring
- `test`: Test changes
- `chore`: Maintenance

## Rules

- Keep the subject imperative and concise.
- Commit only intentional files; do not include `.env`, cache files, build output, or unrelated worktree changes.
- Mention verification commands in the body when useful.
- Use normal shell syntax on this macOS/zsh workspace:

```bash
git add path/to/file
git commit -m "docs(agents): add Signal agent kit"
```

Default prompt: Review the intended changes and create a focused conventional commit.
