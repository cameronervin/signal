import type { Tier } from "@/types/lead";

interface Props {
  tier: Tier;
}

export function TierBadge({ tier }: Props) {
  return (
    <span className={`tier-badge ${tier.toLowerCase()}`}>
      {tier}
    </span>
  );
}
