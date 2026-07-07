# Frontend Design

Use this skill for Signal UI implementation or visual QA.

## Grounding

Read first:
- `backstage/design/README.md`
- `frontend/src/app/globals.css`
- Existing components in `frontend/src/components/ui/`
- Existing shell in `frontend/src/components/layout/`

## Signal Design Principles

- Build the actual SDR workspace, not a landing page.
- Help reps answer: who to work first, what to say, and how urgently to act.
- Use the established purple Signal system, white surfaces, near-black sidebar, mono numerics, tier badges, score meters, flags, and source chips.
- Keep screens dense, quiet, and easy to scan.
- Preserve explicit gate-failed, empty, loading, error, and awaiting-review states.
- Do not add third-party company/client brand names to UI copy or fixtures.

## Implementation Rules

- Use local primitives before adding new ones.
- Use `lucide-react` for icons when available.
- Inline SVG is acceptable for the Signal mark or custom graph visuals.
- Do not paste prototype HTML into the app.
- Avoid decorative blobs, unrelated gradients, or one-note palettes.
- Keep text inside its containers at desktop and narrow widths.
- Preserve keyboard focus and accessible names.

## Verification

Run:

```bash
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend typecheck
```

For substantial UI work, also manually check desktop and narrow layouts and mention any unverified visual risk.
