# Handoff: Signal — Inbound Lead Intelligence

## Overview
**Signal** is an SDR-facing tool that scores, ranks, and enriches inbound multifamily-leasing leads, drafts personalized outreach with cited sources, and runs the work through a human-in-the-loop agent pipeline. Every screen maps to one of three SDR decisions: **who to work first, what to say, how urgently to act.**

This package covers the design system foundations plus six product screens:
1. Dashboard (KPIs + charts)
2. Inbound Leads (ranked queue table)
3. Lead Detail / Row View (enrichment + knowledge graph + drafted email)
4. Digital Workforce (SDR digital worker profile and eligible lead handoffs)
5. Digital Worker Progress (assignment progress preview and SDR check-ins)
6. Gate-Failed Lead State

## About the Design Files
The file in this bundle (`Signal — Design System & Screens.dc.html`) is a **design reference created in HTML** — a prototype showing intended look and behavior, **not production code to copy directly**. It uses inline styles because it was authored in a streaming-preview environment; treat the markup as a precise visual spec, not as shippable components.

The task is to **recreate these designs in the target codebase** (a **Next.js** frontend, per the project plan) using its established patterns and libraries — component primitives, a theme/token layer, and real data-viz libraries. Do not paste the HTML into the app.

## Fidelity
**High-fidelity.** Final colors, typography, spacing, radii, and shadows are specified below and should be reproduced faithfully. Two exceptions are intentionally placeholder and must be re-implemented with real libraries against live data:
- **Charts** (dashboard) — CSS-drawn bars. Use Recharts or visx.
- **Knowledge graph** (lead detail) — hand-placed SVG nodes. Use React Flow (or similar).

## Branding note
The visual system is inspired by the client's brand (**purple accent on near-black + white** — validated against the live marketing site; the earlier green was incorrect). The prototype uses **Figtree** as a free stand-in for the brand's actual typeface, **Proxima Nova**. In the real app, license and use **Proxima Nova** for UI text; keep **JetBrains Mono** for numerics/IDs/logs. The product itself must carry **no third-party brand name** — it is "Signal".

---

## Design Tokens

### Color
| Token | Hex | Use |
|---|---|---|
| `brand/ink` | `#0E0B1A` | Sidebar background, darkest brand (near-black indigo) |
| `brand/deep` | `#4A32C4` | Text on tint, secondary brand, icon strokes |
| `brand/primary` | `#6D4DF6` | Primary buttons, active states, A-tier, positive |
| `brand/tint` | `#EEEBFE` | Soft purple fills (badges, chips, highlights) |
| `brand/tint-2` | `#F5F3FE` | Lightest purple surface (source chips) |
| `brand/border-purple` | `#DDD5FB` | Border on purple surfaces |
| `sidebar/icon-active` | `#B9A6FF` | Active nav icon stroke (on ink) |
| `sidebar/icon-idle` | `#8E88B0` | Idle nav icon stroke (on ink) |
| `ink/900` | `#0F1613` | Primary text |
| `ink/700` | `#28302C` | Email/body copy |
| `ink/600` | `#56605C` | Secondary text |
| `ink/500` | `#333B37` | Table body copy |
| `ink/400` | `#9AA39E` | Muted text, placeholders |
| `surface/0` | `#FFFFFF` | Cards, top bar |
| `surface/1` | `#F5F7F6` | App content background |
| `surface/2` | `#FAFBFB` | Table header, inset strips |
| `border` | `#EAEEEC` | Card borders |
| `border/row` | `#F2F4F3` | Table row dividers |
| `canvas` | `#ECEEED` | Page/canvas behind frames (prototype only) |
| `tier/A` | `#6D4DF6` | A-tier dot (brand purple = top) |
| `tier/B` | `#F5A623` | B-tier dot |
| `tier/C` | `#98A29C` | C-tier dot |
| `amber/text` | `#9A6207` | B-tier / warning text |
| `amber/bg` | `#FEF3DA` | B-tier / warning fill |
| `amber/border` | `#F7E2B0` | B-tier / warning border |
| `danger/text` | `#B4272B` | Flags, gate-fail text |
| `danger/500` | `#E5484D` | Flag dot |
| `danger/bg` | `#FDECEC` / `#FDF5F5` | Flag chip / gate-fail panel |
| `danger/border` | `#F6D2D3` | Flag border |

### Typography
- **UI / display:** Figtree in prototype → **Proxima Nova** in app. Weights used: 400, 500, 600, 700, 800.
- **Mono:** JetBrains Mono, weights 400/500/600 — scores, unit counts, IDs, timestamps, activity log, axis labels, section eyebrows.

| Role | Size / weight | Notes |
|---|---|---|
| Page title | 20px / 800, letter-spacing −0.01em | Top bar |
| Cover title | 30px / 800, −0.02em | Prototype cover only |
| Card title | 14.5px / 700 | Section headers inside cards |
| Heading | 19px / 700 | — |
| Label / control | 13–14px / 600 | Buttons, table cells, nav |
| Body | 13.5px / 400, line-height 1.6 | Email + long copy |
| Small / meta | 11–12px / 500–600 | Secondary lines, chips |
| Eyebrow (mono) | 10px / 600, letter-spacing 0.05em, uppercase, `ink/400` | Field labels |
| Stat (mono) | 17–26px / 600 | KPI numbers, market signals |
| Score (mono) | 14–18px / 600 | Table score, header score |

### Spacing / radii / shadow
- **Spacing scale:** 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 26, 30 px. Card padding typically `20px 22px`; screen gutters `30px`.
- **Radii:** chips/badges 6–8px · buttons/inputs 9px · cards 12–13px · frames 16–18px · icon tiles 8–12px · avatars/dots 50%.
- **Card shadow:** `0 1px 2px rgba(15,22,19,.04), 0 18px 40px rgba(15,22,19,.05)` (used on frame-level cards in the prototype; inner cards use just the border).
- **Primary-button shadow:** `0 2px 6px rgba(22,179,100,.28)`.

---

## App Shell (shared chrome)

Present on every screen except the foundations panel.

- **Left sidebar:** fixed `70px` wide, `brand/ink` (`#0E0B1A`), vertical flex, `18px 0` padding.
  - Top: logo mark — `38px` rounded-`11px` square, `brand/primary` fill, white "signal wave" glyph. `26px` bottom margin.
  - Nav group (`8px` gap): three `44px` rounded-`12px` icon buttons. **Active** item = `rgba(109,77,246,.18)` fill + `1px solid rgba(109,77,246,.55)` border, icon stroke `#B9A6FF`. **Idle** = transparent, icon stroke `#7FA394`.
    - **Home** icon → `/dashboard`
    - **Inbox** icon → `/leads`
    - **Grid (2×2)** icon → `/agents`
  - Bottom (margin-top:auto): `32px` avatar circle, `brand/deep` bg, `#BFF3D6` initials "SD".
- **Top bar:** `66px` tall, `surface/0`, `1px solid border` bottom, `0 30px` padding, space-between. Left = page title (+ optional count subtitle). Right = contextual controls (date range / Filter / Search / avatar).
- **Content region:** `surface/1` (`#F5F7F6`) background, scrollable, `~26px 30px` padding.

**Icon SVGs** (24×24 viewBox, `stroke-width:2`, round caps/joins; recreate with your icon lib — lucide equivalents: `home`, `inbox`, `layout-grid`):
- Home: `M4 10.5L12 4l8 6.5` + `M6 9.5V19a1 1 0 001 1h10a1 1 0 001-1V9.5` + `M10 20v-5h4v5`
- Inbox: `M22 12h-6l-2 3h-4l-2-3H2` + `M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z`
- Grid: four `7×7` rounded-`1.6` rects at (4,4)(13,4)(4,13)(13,13)

---

## Reusable Components

Build these primitives first; every screen composes from them.

### TierBadge
Pill: mono 11px/600, `4px 9px` padding, radius 7px, `6px` gap, leading `6px` dot.
- A: text `#4A32C4`, bg `#EEEBFE`, border `#DDD5FB`, dot `#6D4DF6`
- B: text `#9A6207`, bg `#FEF3DA`, border `#F7E2B0`, dot `#F5A623`
- C: text `#5A635E`, bg `#F0F2F1`, border `#E1E5E3`, dot `#98A29C`
- Compact table variant: font 11px, `3px 8px`, radius 6px, `5px` dot.

### ScoreMeter
Row: mono score (14px/600) + `40×6px` track (`#EEF1F0`, radius 3) with fill at `score%` in the tier color. Large variant (foundations) = 120px track, 7px tall.

### SourceChip
Inline: 11px/500, `#4A32C4` text, bg `#F5F3FE`, **dashed** `1px #C9BEF7` border, radius 7px, `4px 9px`. Leads with a mono 9.5–10px/600 label (`NewsAPI`, `Census`, `FRED`) then the value.

### Flag
Inline pill: 11.5px/600. Danger = text `#B4272B`, bg `#FDECEC`, border `#F6D2D3`. Warning = amber tokens. Leading `⚑` glyph.

### Button
Radius 9px, 13px/600, `9px 15–17px` padding, `7px` icon gap.
- **Primary:** `#6D4DF6` bg, white text, shadow `0 2px 6px rgba(109,77,246,.28)`.
- **Secondary:** white bg, `1px solid #E4E8E6`, `#0F1613` text.
- **Ghost/purple:** transparent or white, `#4A32C4` text (used on purple panels with `#DDD5FB` border).
- Small table variant: 12px/600, `6px 11px`.

### SearchInput
`1px solid #E4E8E6`, white, radius 9px, `8px 12px`, `8px` gap, leading search glyph (`#9AA39E`), placeholder 13px `#9AA39E`. Prototype width ~240px.

### FilterButton
Secondary button with a "sliders" glyph (`M3 5h18 / M6 12h12 / M10 19h4`).

### DataTable
- Header row: `surface/2` bg, `1px border` bottom, mono 10px/600, uppercase, letter-spacing 0.06em, `#9AA39E`, `12px 18–20px` padding.
- Body rows: `13px 18–20px` padding, `1px solid #F2F4F3` divider, CSS-grid columns with `14–16px` gap, `align-items:center`.
- Row states: default white; **A-tier row** subtle tint `#FAF9FE`; **hover** → light purple tint (add in app); **disabled/gate-failed** → `#FCFCFB` bg + `opacity .6–.92`.
- Trailing chevron column (`34px`) with a `M9 6l6 6-6 6` chevron, `#9AA39E` (muted `#C7CDC9` when row is inert).

### StatCard / KPICard
White, `1px border`, radius 12–13px, `13–16px 16–18px` padding. Label 11.5–12px/600 `#7A847F`; value mono 26px/600; delta 11.5px/600 (`#4A32C4` up-good, `#9A6207` caution).

### PipelineStepper (worker progress)
Vertical. Each step = flex row: a `22px` rail column (status dot + `2px` connector that flex-fills to next dot) + content (title 13.5/600, mono duration right, sub-detail/chips).
- Done dot: `20px` circle `#6D4DF6`, white `✓`. Connector below = `#6D4DF6`.
- Active dot: `20px` white circle, `2px #6D4DF6` border, `7px` inner purple dot. Connector = `#E1E5E3`.
- Pending dot: `20px` `#EEF1F0` circle, `1px #E1E5E3` border; label + text muted `#9AA39E`.

---

## Screens / Views

> Frame size in prototype: `1460px` wide; content column is `1440px − 70px sidebar`. Design target is a desktop app ~1440px; make it fluid below the sidebar.

### 1. Dashboard — `/dashboard` (Home active)
**Purpose:** at-a-glance queue health and where opportunity concentrates.
**Layout:** top bar (title "Dashboard" + right: "Last 14 days" dropdown chip + avatar). Content = vertical stack, `20px` gaps:
- **KPI row:** 5 equal `StatCard`s — New leads today `42` (▲8); A-tier in queue `11` (SLA: touch <15 min, amber); Median speed-to-lead `14m` (▼ from 41m baseline); Drafts sent 7d `128` (Avg 4 edits/draft); First-touch response `34%` (▲6 pts).
- **Charts row** (grid `1.5fr 1fr`):
  - *Inbound volume by tier* — stacked bars, ~14 days, A `#6D4DF6` / B `#F5A623` / C `#D3D9D6`, with legend + mono date axis. **→ Recharts stacked bar.**
  - *Score distribution* — histogram, 187 leads, gradient buckets from grey→amber→purple; footer legend C 61% / B 24% / A 15%. **→ Recharts/visx histogram.**
- **Top markets by opportunity** — card, 2-column list of horizontal bars: Austin 91, Charlotte 84, Nashville 79, Phoenix 73, Denver 68, Seattle 64 (label 130px, `8px` track `#EEF1F0`, fill in purple ≥75 else amber, mono value). "View all markets →" link `#0B6B45`.

### 2. Inbound Leads — `/leads` (Inbox active)
**Purpose:** the ranked work queue; rep starts at row one.
**Layout:** top bar (title + "187 open · sorted by tier" + right: Filter + Search). Filter-chip row (`Tier A · 11` active purple, `Corporate email`, `Unassigned`, `+ Add filter`). Then a `DataTable`.
**Columns** (grid `56px 1.5fr 1.4fr 1.1fr 72px 96px 2.1fr 150px 34px`): Tier · Lead (name + role) · Company · Market · Units (mono) · Score (`ScoreMeter`) · Why this lead · Draft action · chevron.
**Rows (sample data):**
- Sarah Chen · VP Leasing · Greystar · Austin TX · 794k · **92 A** · "Top-50 operator · acquisition news 3d ago · 8% rent growth" · [Copy draft]. Row tinted `#FAF9FE`.
- Marcus Webb · Dir Operations · Cortland · Charlotte NC · 85k · **84 A** · "61% renter share · tight labor market · senior title".
- Priya Nair · Regional Mgr · Bozzuto · Arlington VA · 44k · **78 A** · "High-density submarket · repeat inbound (+10)".
- Robert Diaz · VP Portfolio · Avenue5 · Seattle WA · 85k · **74 B** · "3rd-party manager · mixed asset types · solid market".
- David Okafor · Asset Mgr · MAA · Nashville TN · 102k · **71 B** · "REIT scale · mid-seniority title · strong Sun Belt growth".
- Lin Zhao · Dir Leasing · Willow Bridge · Phoenix AZ · 180k · **69 B** · "Large footprint · rent trend flat · no recent trigger".
- Jenna Cole · Property Mgr · Camden · Denver CO · 58k · **64 B** · "Site-level title · single property · good renter density".
- **Gate-failed C:** Tom Whitaker · ⚑ personal email gmail.com · Unverified · Miami FL · — · **28 C** · "Gate failed: no corporate domain · company won't resolve" · action = red "Review flags" (no Copy draft). Row `#FCFCFB`, dim, muted chevron.
**Draft action** = secondary small button with a copy glyph, label "Copy draft".
**Interaction:** row click / chevron → `/leads/[id]`. Draft button copies the generated email to clipboard (toast confirm).

### 3. Lead Detail / Row View — `/leads/[id]` (Inbox active)
**Purpose:** everything needed to work one lead + review its draft.
**Layout:** header bar = back chevron + name "Sarah Chen" + A-tier badge "A-TIER · 92" + subline "VP, Leasing · Greystar · Austin, TX"; right = "Dismiss" (secondary) + "Assign Digital Worker" (primary, `+` glyph). Body = 2-col grid `1fr 1fr`, `16px` gap.
**Left column (stack):**
- *Lead & enrichment* card: 2×2 field grid (Contact `sarah.chen@greystar.com` "✓ Corporate domain · valid MX"; Seniority "VP · executive tier" "Fit 15/15"; Company "Greystar Real Estate" "NMHC #1 · 794k units · conventional MF"; Property "The Domain · Austin, TX" "Walk Score 78 · tract 48453"). Divider → **Market signals** 4-stat mono row (Renter 61% / Rent YoY +8.1% / Unemployment 3.2% / HH growth +4.4%, all `#0B6B45`). Divider → **Talking points** — 3 bullets with green `›` markers.
- *Knowledge graph* card: header + "2 related leads" chip. Left = mini node-link (center node "Sarah Chen" purple circle; satellites Greystar / The Domain / Austin metro / RealPage, connected by `#D3E7DC` edges). Right = **Related leads** list (Alan Reyes — Greystar, 2nd inbound this quarter; Nadia Owens — same Austin submarket, 3 leads/30d) + "Expand graph →". **→ React Flow for the node-link.**
**Right column:** *Drafted email* card, full height, sectioned:
- Header: "Drafted email" + "Review & handoff" tag + "✎ Editable".
- Meta rows: From "You · Signal SDR" / To `sarah.chen@greystar.com` / Subj "Scaling leasing after the Austin expansion".
- Body: editable email; **personalization spans highlighted** with `#EEEBFE` bg + `2px solid #6D4DF6` bottom-border (the Austin expansion; 61% renters; rents up 8%).
- Sources strip (`surface/2`): eyebrow + `SourceChip`s — NewsAPI "Greystar Austin expansion · 3d ago", Census "61% renters", FRED "rent +8% YoY".
- Actions: "Regenerate" (secondary, refresh glyph) left; "Copy" + "Open Digital Workforce" (primary) right.
**Note:** the email pane is the draft review area from the wireframe — implement as an editable rich-text/preview region, not a literal iframe unless you sandbox external HTML.

### 4. Digital Workforce — `/agents` (Grid active)
**Purpose:** preview the SDR Digital Worker that can be assigned to eligible
inbound leads in a future workflow.
**Layout:** top bar title "Digital Workforce" with eligible lead count and
search. Content starts with a worker profile for **SDR Digital Worker**, a
preview-only status pill, and capability cards for Email, Text messaging, and
Human review. A preview note explains that backend assignment, communication
tools, and persistence are deferred.
**Lead handoffs:** table of draft-ready, gate-passed inbound leads with score,
channel readiness, assignment preview summary, disabled "Assign" controls, and
non-mutating "Preview" links to `/agents/[previewId]`.

### 5. Digital Worker Progress — `/agents/[previewId]` (Grid active)
**Purpose:** preview what the human SDR can check after assigning the SDR Digital
Worker, without triggering backend assignment or live communication.
**Layout:** header = back chevron + "Digital worker progress" + preview-only
status + disabled "Assign worker" button. Metadata strip shows Worker, Lead,
Channels, and Review. Body = 2-col grid `1fr 1fr`:
- **Left — Worker assignment preview** card: `PipelineStepper` with
  communication-oriented steps: Assignment intake, Outreach plan, Email draft
  check, Text follow-up readiness, SDR check-in.
- **Right (stack):**
  - *Check-in log* card: preview activity that states no assignment is persisted
    and no outreach is sent.
  - *SDR review required* panel: score/tier summary, email/text/readiness notes,
    disabled "Assign worker" control, and "View lead" link.

### 6. Gate-Failed Lead State — `/leads/[id]` variant (Inbox active)
**Purpose:** tell the rep what **not** to work, and why; suppress the draft.
**Layout:** header = back + "Tom Whitaker" + C-tier badge "C-TIER · 28" + "Unverified company · Miami, FL". Body grid `1fr 1fr`:
- **Left (stack):** *Hard gates failed* panel (danger: bg `#FDF5F5`, border `#F6D2D3`) with warning-triangle title "Hard gates failed — do not work this lead" and 3 items (✕ no corporate email domain / gmail.com; ✕ company won't resolve; ! portfolio unverifiable → scoring suppressed). Then a *Why flags matter* card explaining the ROI of telling reps what not to work + domain-reputation risk.
- **Right:** empty-output card, centered — struck-through inbox glyph, "No draft generated", explanation, actions "Dismiss lead" / "Verify manually" (both secondary).

---

## Interactions & Behavior
- **Navigation:** sidebar items route between the five sections; lead rows and agent rows open their detail routes; back chevrons return to the queue/list.
- **Copy draft:** copies generated email text to clipboard → toast.
- **Assign Digital Worker:** opens `/agents?leadId=<id>` from lead detail and
  highlights the preview handoff. It does not mutate state in this frontend-only
  slice.
- **Table pagination:** `/leads` and `/agents` paginate their already-loaded
  table rows client-side with `?page=<n>` URL state. Filters and search reset the
  table to page 1 while preserving unrelated query params such as `leadId`.
- **Worker progress preview:** `/agents/[previewId]` shows communication-oriented
  handoff steps and check-in logs. Assignment, email, text messaging, and send
  actions remain disabled until backend support exists.
- **Hover states:** table rows get a light-purple hover tint; buttons darken ~6–8%; chevrons/links shift toward `#4A32C4`.
- **Empty / gate-failed / awaiting states:** shown explicitly (screens 5–6) — reproduce as first-class states, not afterthoughts.
- **Transitions:** keep subtle (150–200ms ease) for row hover, button press, route changes. No large motion.
- **Responsive:** desktop-first (SDR workstation). Below ~1100px, collapse the two-column detail grids to a single column; keep the sidebar fixed.

## State Management
- **Leads:** list with `{id, tier, name, role, company, market, units, score, whyLine, flags[], enrichment{}, draft{subject, body, sources[]}, related[]}`; sorted by score desc within tier. Filters: tier, corporate-email, unassigned, search query.
- **Digital Workforce:** frontend-only profile and preview data:
  `{workerId, displayName, capabilities[], reviewMode}` plus handoffs
  `{previewId, leadId, channelReadiness, assignmentStatus, steps[], activityLog[]}`.
- **Data fetching:** enrichment/scoring/draft come from the FastAPI + LangGraph backend (deterministic-enrichment → agent → graph nodes). The run-detail activity log and pipeline states should stream/poll from the run status endpoint. Charts + KPIs read from an analytics endpoint (hard-coded/static acceptable for v1 per plan).
- **Gates:** a lead failing hard gates renders the gate-failed variant and must **not** expose a draft.

## Assets
- **Icons:** all inline SVG in the prototype; recreate with your icon set (lucide names noted above: `home`, `inbox`, `layout-grid`, `search`, `sliders`, `chevron-right`, `chevron-left`, `send`, `copy`, `refresh-cw`, `alert-triangle`, `check-circle`, `clock`, `plus`). The logo "signal wave" mark is custom — rebuild as a small SVG component.
- **Fonts:** Figtree + JetBrains Mono via Google Fonts in the prototype; in-app use **Proxima Nova** (licensed) + JetBrains Mono.
- **Charts / graph:** no image assets — implement with Recharts/visx (charts) and React Flow (knowledge graph).
- **No third-party brand assets** are used or should be added; the product is "Signal".

## Files
- `Signal — Design System & Screens.dc.html` — the full design reference (foundations panel + 6 screens). Open in a browser to inspect exact values; every screen is labeled (`01 — FOUNDATIONS` … `07 — GATE-FAILED LEAD STATE`).
