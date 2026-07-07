import type { Tier } from "@/types/lead";

interface Props {
  score: number;
  tier: Tier;
  size?: "table" | "large";
}

export function ScoreMeter({ score, tier, size = "table" }: Props) {
  return (
    <span className={`score-meter ${size === "large" ? "large" : ""}`}>
      <span className="score-meter-value">{score}</span>
      <span className="meter-track">
        <span className={`meter-fill tier-${tier.toLowerCase()}`} style={{ width: `${score}%` }} />
      </span>
    </span>
  );
}
