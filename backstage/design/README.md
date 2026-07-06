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
4. Agent Assignment - active runs.
5. Agent Progress - pipeline and activity log.
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
| `source-border` | `#C9BEF7` |
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
| `control-border` | `#E4E8E6` |
| `track` | `#EEF1F0` |
| `tier-a` | `#6D4DF6` |
| `tier-b` | `#F5A623` |
| `tier-c` | `#98A29C` |
| `tier-c-text` | `#5A635E` |
| `tier-c-bg` | `#F0F2F1` |
| `tier-c-border` | `#E1E5E3` |
| `amber-text` | `#9A6207` |
| `amber-bg` | `#FEF3DA` |
| `amber-border` | `#F7E2B0` |
| `danger-text` | `#B4272B` |
| `danger-500` | `#E5484D` |
| `danger-bg` | `#FDECEC` |
| `danger-panel` | `#FDF5F5` |
| `danger-border` | `#F6D2D3` |
| `success-text` | `#0B6B45` |
| `success-soft` | `#EDF8F2` |
| `graph-edge` | `#D3E7DC` |
| `muted-chev` | `#C7CDC9` |
| `soft-purple-row` | `#FAF9FE` |
| `row-dimmed` | `#FCFCFB` |
| `card-shadow` | `0 1px 2px rgba(15, 22, 19, 0.04), 0 18px 40px rgba(15, 22, 19, 0.05)` |
| `button-shadow` | `0 2px 6px rgba(109, 77, 246, 0.28)` |

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
