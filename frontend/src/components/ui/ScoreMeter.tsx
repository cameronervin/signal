import type { Tier } from "@/types/lead";

interface Props {
  score: number;
  tier: Tier;
  size?: "table" | "large";
}

export function ScoreMeter({ score, tier, size = "table" }: Props) {
  return (
    <span className="flex items-center gap-2">
      <span className={`mono font-semibold ${size === "large" ? "text-lg" : "w-6 text-sm"}`}>{score}</span>
      <meter
        aria-label={`Score ${score}`}
        className={`score-meter tier-${tier.toLowerCase()} ${size === "large" ? "large" : ""}`}
        max={100}
        min={0}
        value={score}
      />
    </span>
  );
}
