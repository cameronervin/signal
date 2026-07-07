# Signal Design Tokens

Source of truth: `backstage/design/README.md` and `frontend/src/app/globals.css`.

## Color

| Token | Value | Use |
| --- | --- | --- |
| `brand-ink` | `#0E0B1A` | Sidebar and darkest shell |
| `brand-deep` | `#4A32C4` | Secondary brand text and strokes |
| `brand-primary` | `#6D4DF6` | Primary buttons, active states, A-tier |
| `brand-tint` | `#EEEBFE` | Soft purple fills |
| `brand-tint-2` | `#F5F3FE` | Light purple source surfaces |
| `border-purple` | `#DDD5FB` | Purple borders |
| `surface-0` | `#FFFFFF` | Cards and top bar |
| `surface-1` | `#F5F7F6` | App content background |
| `surface-2` | `#FAFBFB` | Table headers and inset strips |
| `ink-900` | `#0F1613` | Primary text |
| `ink-600` | `#56605C` | Secondary text |
| `ink-400` | `#9AA39E` | Muted text |
| `border` | `#EAEEEC` | Card borders |
| `tier-a` | `#6D4DF6` | A-tier |
| `tier-b` | `#F5A623` | B-tier |
| `tier-c` | `#98A29C` | C-tier |
| `danger-text` | `#B4272B` | Gate and flag text |
| `danger-bg` | `#FDECEC` | Flag background |

## Type

- UI/display: Proxima Nova when available, with Figtree/system fallback already declared.
- Mono: JetBrains Mono for scores, ids, timestamps, and metric numerics.
- Do not scale font size with viewport width.
- Letter spacing should remain `0` except documented mono eyebrows.

## Shape And Motion

- Buttons and inputs: 9px radius.
- Chips and badges: 6-8px radius.
- Cards: 12-13px radius.
- Sidebar nav: 12px radius.
- Transitions: 150-200ms ease for hover and press states.
- Motion must honor reduced-motion preferences.

## Rules

- Prefer CSS variables from `frontend/src/app/globals.css`.
- Avoid repeated arbitrary colors.
- Do not introduce decorative gradients, blobs, or unrelated brand palettes.
- Keep UI neutral: no third-party company/client brand names in copy, fixtures, docs, comments, tests, or env examples.
