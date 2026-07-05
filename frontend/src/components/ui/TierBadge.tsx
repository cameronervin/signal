import type { Tier } from "@/types/lead";

interface Props {
  tier: Tier;
}

const tierStyles: Record<Tier, { text: string; bg: string; border: string; dot: string }> = {
  A: {
    text: "var(--brand-deep)",
    bg: "var(--brand-tint)",
    border: "var(--border-purple)",
    dot: "var(--tier-a)"
  },
  B: {
    text: "var(--amber-text)",
    bg: "var(--amber-bg)",
    border: "var(--amber-border)",
    dot: "var(--tier-b)"
  },
  C: {
    text: "var(--tier-c-text)",
    bg: "var(--tier-c-bg)",
    border: "var(--tier-c-border)",
    dot: "var(--tier-c)"
  }
};

export function TierBadge({ tier }: Props) {
  const style = tierStyles[tier];
  return (
    <span
      className="mono inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-[11px] font-bold"
      style={{ background: style.bg, borderColor: style.border, color: style.text }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: style.dot }} />
      {tier}
    </span>
  );
}
