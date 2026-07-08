# Signal Design System

Signal is a desktop-first SDR workspace with a near-black sidebar, white work
surfaces, compact tables, explicit review states, and purple as the primary
action and A-tier accent.

The design reference is a visual spec, not production code to paste. Use
Next.js components, local primitives, and real chart/graph libraries when those
views move beyond scaffold state.

Detailed implementation guidance lives in
`backstage/design/signal-design-handoff.md`.

## Screens

1. Dashboard - KPIs and queue health.
2. Inbound Leads - ranked table.
3. Lead Detail - enrichment, graph context, draft review.
4. Digital Workforce - SDR digital worker preview and eligible lead handoffs.
5. Digital Worker Progress - communication handoff preview and SDR check-in log.
6. Gate-Failed Lead - flags and no-draft state.

## Tokens

| Token | Value |
| --- | --- |
| `brand-ink` | `#0E0B1A` |
| `brand-deep` | `#4A32C4` |
| `brand-primary` | `#6D4DF6` |
| `brand-tint` | `#EEEBFE` |
| `brand-tint-2` | `#F5F3FE` |
| `border-purple` | `#DDD5FB` |
| `sidebar-icon-active` | `#B9A6FF` |
| `sidebar-icon-idle` | `#8E88B0` |
| `surface-0` | `#FFFFFF` |
| `surface-1` | `#F5F7F6` |
| `surface-2` | `#FAFBFB` |
| `ink-900` | `#0F1613` |
| `ink-700` | `#28302C` |
| `ink-600` | `#56605C` |
| `ink-500` | `#333B37` |
| `ink-400` | `#9AA39E` |
| `border` | `#EAEEEC` |
| `row-border` | `#F2F4F3` |
| `track` | `#EEF1F0` |
| `amber-text` | `#9A6207` |
| `amber-bg` | `#FEF3DA` |
| `amber-border` | `#F7E2B0` |
| `danger-text` | `#B4272B` |
| `danger-500` | `#E5484D` |
| `danger-bg` | `#FDECEC` |
| `danger-panel` | `#FDF5F5` |
| `danger-border` | `#F6D2D3` |
| `success-text` | `#0B6B45` |

## Component Priorities

- `TierBadge`
- `ScoreMeter`
- `SourceChip`
- `Flag`
- `Button`
- `SearchInput`
- `DataTable`
- `MetricCard`
- `PipelineStepper`

## Implementation Notes

- Use lucide-react icons.
- Use Recharts or visx for charts.
- Use React Flow for the knowledge graph.
- Keep gate-failed states first-class.
- Below 1100px, detail pages collapse to one column.
- Keep all implementation copy Signal-neutral.
