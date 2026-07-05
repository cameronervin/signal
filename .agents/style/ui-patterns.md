# Signal UI Patterns

## App Shell

- Fixed 70px sidebar with Signal mark and three nav icons.
- 66px top bar with title, subtitle, and contextual controls.
- Product surfaces start immediately. Do not build a landing page.

## Components

- Use local primitives in `frontend/src/components/ui/`.
- Use lucide-react for common icons.
- Use React Flow for the knowledge graph when the detail view is implemented.
- Use Recharts or visx for charts.
- Use Radix for dialogs, menus, tabs, switches, and tooltips.

## States

Build first-class states for:

- A/B/C tiers.
- Gate-failed leads.
- Awaiting human review.
- Public API fallback or cached data.
- Empty queues and no related leads.

## Copy

Copy is direct and operational. It should help the SDR decide who first, what
to say, or how urgently to act.
