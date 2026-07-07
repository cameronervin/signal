# Frontend Design Standards

For Signal UI work, read `backstage/design/README.md` before editing.

## Visual System

- Use Signal's purple-on-near-black and white workspace system from `frontend/src/app/globals.css`.
- Prefer existing CSS variables: `--brand-ink`, `--brand-deep`, `--brand-primary`, `--brand-tint`, `--surface-*`, `--ink-*`, `--border`, `--tier-*`, `--amber-*`, and `--danger-*`.
- Preserve desktop-first SDR workstation density.
- Use card radii, spacing, mono numerics, score meters, tier badges, flags, and source chips as documented.
- Do not add third-party company or client brand names to copy, fixtures, docs, comments, or tests.

## Components

- Use local primitives in `frontend/src/components/ui/`.
- Use `lucide-react` for normal icons.
- Inline SVG is allowed for the Signal mark and truly custom graph/visual primitives.
- Do not paste prototype HTML into the app.
- Use Recharts/visx-style charting and React Flow-style graphing only when those dependencies are explicitly added by a plan.

## UX Rules

- First screen should be the usable SDR workspace, not a marketing landing page.
- Gate-failed leads have a clear no-draft state.
- Send-like actions remain explicit and review-gated.
- Detail grids collapse below narrow desktop widths without text overlap.
- Motion should be subtle and honor reduced-motion preferences.
