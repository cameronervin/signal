import { agentRuns as fixtureAgentRuns, getAgentRun as getFixtureAgentRun } from "@/lib/fixtures/leads";
import type { FixtureAgentRun } from "@/types/lead";

export async function listAgentRuns(): Promise<FixtureAgentRun[]> {
  return fixtureAgentRuns;
}

export async function getAgentRun(runId: string): Promise<FixtureAgentRun | undefined> {
  return getFixtureAgentRun(runId);
}
