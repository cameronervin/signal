# Signal Design Handoff

This handoff translates the design reference into Signal-owned implementation
guidance. Treat the reference as a visual spec, not production code to paste.

## Product Intent

Signal is a desktop-first SDR workspace for deciding:

- Who to work first.
- What to say.
- How urgently to act.

Every surface should feel operational, compact, and review-oriented. The first
screen is the product workspace, not a marketing page.

## Foundations

### Color

| Token | Hex | Use |
| --- | --- | --- |
| `brand-ink` | `#0E0B1A` | Sidebar and deepest shell |
| `brand-deep` | `#4A32C4` | Text on tinted surfaces, secondary icons |
| `brand-primary` | `#6D4DF6` | Primary actions, active states, A-tier |
| `brand-tint` | `#EEEBFE` | Badges, chips, highlighted personalization |
| `brand-tint-2` | `#F5F3FE` | Source chips and light purple panels |
| `border-purple` | `#DDD5FB` | Purple panel borders |
| `sidebar-icon-active` | `#B9A6FF` | Active sidebar icons |
| `sidebar-icon-idle` | `#8E88B0` | Idle sidebar icons |
| `ink-900` | `#0F1613` | Primary text |
| `ink-700` | `#28302C` | Long-form copy and draft body |
| `ink-600` | `#56605C` | Secondary text |
| `ink-500` | `#333B37` | Table body copy |
| `ink-400` | `#9AA39E` | Muted text and placeholders |
| `surface-0` | `#FFFFFF` | Cards and top bar |
| `surface-1` | `#F5F7F6` | App background |
| `surface-2` | `#FAFBFB` | Table headers and insets |
| `border` | `#EAEEEC` | Card borders |
| `row-border` | `#F2F4F3` | Table row dividers |
| `track` | `#EEF1F0` | Meters and progress tracks |
| `tier-a` | `#6D4DF6` | A-tier |
| `tier-b` | `#F5A623` | B-tier |
| `tier-c` | `#98A29C` | C-tier |
| `amber-text` | `#9A6207` | Caution and in-progress text |
| `amber-bg` | `#FEF3DA` | Caution fills |
| `amber-border` | `#F7E2B0` | Caution borders |
| `danger-text` | `#B4272B` | Gate failure text |
| `danger-500` | `#E5484D` | Gate failure dot |
| `danger-bg` | `#FDECEC` | Danger chips |
| `danger-panel` | `#FDF5F5` | Gate failure panels |
| `danger-border` | `#F6D2D3` | Danger borders |
| `success-text` | `#0B6B45` | Market signals and good links |

### Typography

- UI: Proxima Nova when licensed, with Figtree and system sans fallbacks.
- Mono: JetBrains Mono for scores, IDs, unit counts, timestamps, activity logs,
  and stat values.
- Page titles: 20px, 800 weight.
- Card titles: 14.5px, 700 weight.
- Controls and table cells: 13px to 14px, 600 weight.
- Body copy: 13.5px, 400 weight, 1.6 line-height.
- Eyebrows: 10px mono, uppercase, 0.05em letter spacing.
- Avoid viewport-scaled type. Use zero letter spacing except mono eyebrows.

### Shape, Spacing, and Motion

- Spacing scale: 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 26, 30 px.
- Chips and badges: 6 to 8px radius.
- Buttons and inputs: 9px radius.
- Cards: 12 to 13px radius.
- Icon tiles: 8 to 12px radius with stable square dimensions.
- Screen gutters: 30px on desktop.
- Card shadow: `0 1px 2px rgba(15,22,19,.04), 0 18px 40px rgba(15,22,19,.05)`.
- Primary button shadow: `0 2px 6px rgba(109,77,246,.28)`.
- Transitions: 150ms to 200ms ease. Respect reduced motion.

## Shared Chrome

- Sidebar: fixed 70px column, near-black background, three 44px icon buttons,
  active purple tint, and a small custom Signal wave mark.
- Top bar: 66px high, white surface, bottom border, page title/subtitle on the
  left and contextual controls on the right.
- Content region: app background with 26px by 30px padding.
- Below 1100px, detail grids collapse to a single column.

## Reusable Components

- `TierBadge`: mono pill with leading dot and A/B/C color variants.
- `ScoreMeter`: mono score plus tier-colored progress track.
- `SourceChip`: dashed purple source chip with a mono source label.
- `Flag`: danger or warning pill for gate and quality flags.
- `Button`: primary, secondary, ghost, and small table variants.
- `SearchInput`: icon, placeholder, white surface, and tokenized border.
- `DataTable`: tokenized header, row dividers, A-tier tint, hover tint, and
  disabled/gate-failed state.
- `MetricCard`: compact KPI card with mono stat value and colored delta.
- `PipelineStepper`: done, active, and pending steps that preserve the human
  review gate before send-like actions.

## Screen Guidance

- Dashboard: KPI row, tier volume chart placeholder, score distribution, and top
  markets. Use real chart libraries when analytics move beyond scaffold data.
- Inbound leads: ranked queue with filter chips, search, tier/score cells, why
  line, and copy-or-review action. Gate-failed rows must not expose draft copy.
- Lead detail: left-side enrichment, market signals, talking points, and graph
  context; right-side cited draft review for gate-passed leads.
- Agent assignment: active run table with agent icon tiles, segmented stage
  progress, and first-class "awaiting you" state.
- Agent progress: run metadata, pipeline stepper, activity log, output review
  panel, and explicit human review before send.
- Gate-failed lead: danger panel with gate reasons plus a no-draft empty state.

## Implementation Notes

- Use lucide-react icons where available.
- Use Recharts or visx for production charts.
- Use React Flow for production knowledge graph views.
- Use typed fixtures or API contracts; do not paste the prototype HTML into the
  Next.js app.
- Keep copy Signal-neutral and operational.
