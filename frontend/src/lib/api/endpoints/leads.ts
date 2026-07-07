import { getLead as getFixtureLead, leads as fixtureLeads } from "@/lib/fixtures/leads";
import type { FixtureLead, Tier } from "@/types/lead";

const tierOrder: Record<Tier, number> = {
  A: 0,
  B: 1,
  C: 2
};

export async function listLeads(): Promise<FixtureLead[]> {
  return [...fixtureLeads].sort(
    (leadA, leadB) =>
      tierOrder[leadA.score.tier] - tierOrder[leadB.score.tier] || leadB.score.total - leadA.score.total
  );
}

export async function getLead(id: string): Promise<FixtureLead | undefined> {
  return getFixtureLead(id);
}
