import type { Tier } from "@/types/lead";

interface Props {
  score: number;
  tier: Tier;
  size?: "table" | "large";
}

const tierColor: Record<Tier, string> = {
  A: "var(--tier-a)",
  B: "var(--tier-b)",
  C: "var(--tier-c)"
};

export function ScoreMeter({ score, tier, size = "table" }: Props) {
  return (
    <span className="flex items-center gap-2">
      <span className={`mono font-semibold ${size === "large" ? "text-lg" : "w-6 text-sm"}`}>{score}</span>
      <span className={`meter-track ${size === "large" ? "h-[7px] w-[120px]" : "h-1.5 w-10"}`}>
        <span
          className="meter-fill"
          style={{ width: `${score}%`, background: tierColor[tier] }}
        />
      </span>
    </span>
  );
}
