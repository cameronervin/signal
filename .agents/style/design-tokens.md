# Signal Design Tokens

Source of truth: `backstage/design/README.md` and the design handoff.

## Color

| Token | Value | Use |
| --- | --- | --- |
| `brand-ink` | `#0E0B1A` | Sidebar and deepest shell |
| `brand-deep` | `#4A32C4` | Secondary brand text and icons |
| `brand-primary` | `#6D4DF6` | Primary actions, active state, A-tier |
| `brand-tint` | `#EEEBFE` | Badges, highlighted personalization |
| `brand-tint-2` | `#F5F3FE` | Source chip surfaces |
| `border-purple` | `#DDD5FB` | Purple borders |
| `source-border` | `#C9BEF7` | Source chip borders |
| `sidebar-icon-active` | `#B9A6FF` | Active sidebar icons |
| `sidebar-icon-idle` | `#8E88B0` | Idle sidebar icons |
| `surface-0` | `#FFFFFF` | Cards and top bar |
| `surface-1` | `#F5F7F6` | App background |
| `surface-2` | `#FAFBFB` | Table headers and insets |
| `ink-900` | `#0F1613` | Primary text |
| `ink-700` | `#28302C` | Draft body and long-form copy |
| `ink-600` | `#56605C` | Secondary text |
| `ink-500` | `#333B37` | Table body copy |
| `ink-400` | `#9AA39E` | Muted text |
| `border` | `#EAEEEC` | Card borders |
| `row-border` | `#F2F4F3` | Table row dividers |
| `control-border` | `#E4E8E6` | Inputs and secondary controls |
| `track` | `#EEF1F0` | Meters and progress tracks |
| `tier-a` | `#6D4DF6` | A-tier |
| `tier-b` | `#F5A623` | B-tier |
| `tier-c` | `#98A29C` | C-tier |
| `tier-c-text` | `#5A635E` | C-tier text |
| `tier-c-bg` | `#F0F2F1` | C-tier badge background |
| `tier-c-border` | `#E1E5E3` | C-tier badge border |
| `amber-text` | `#9A6207` | Warning and in-progress text |
| `amber-bg` | `#FEF3DA` | Warning and in-progress fills |
| `amber-border` | `#F7E2B0` | Warning borders |
| `danger-text` | `#B4272B` | Gate failure text |
| `danger` | `#E5484D` | Gate failures |
| `danger-bg` | `#FDECEC` | Danger chips |
| `danger-panel` | `#FDF5F5` | Gate failure panels |
| `danger-border` | `#F6D2D3` | Danger borders |
| `success-text` | `#0B6B45` | Market signal and good-link text |
| `success-soft` | `#EDF8F2` | Soft success surfaces |
| `graph-edge` | `#D3E7DC` | Knowledge graph connector lines |
| `muted-chev` | `#C7CDC9` | Muted chevrons |
| `soft-purple-row` | `#FAF9FE` | A-tier table row tint |
| `row-dimmed` | `#FCFCFB` | Low-priority or blocked row background |
| `card-shadow` | `0 1px 2px rgba(15, 22, 19, 0.04), 0 18px 40px rgba(15, 22, 19, 0.05)` | Elevated cards |
| `button-shadow` | `0 2px 6px rgba(109, 77, 246, 0.28)` | Primary button shadow |

## Type

- UI: Proxima Nova when licensed, fallback to Figtree/system sans.
- Numerics and IDs: JetBrains Mono.
- Do not use viewport-scaled font sizes.
- Letter spacing is `0` except small uppercase mono eyebrows.

## Shape

- Chips: 6-8px radius.
- Buttons and inputs: 9px radius.
- Cards: 12px radius.
- Icon buttons: stable square dimensions.

## Motion

- Hover and press transitions: 150-200ms ease.
- No large motion.
- Respect reduced motion.
