import { AgentAssignmentView } from "@/components/features/agents/AgentAssignmentView";
import { listAgentRuns } from "@/lib/api/endpoints/agent-runs";

export default async function AgentsPage() {
  const agentRuns = await listAgentRuns();

  return <AgentAssignmentView agentRuns={agentRuns} />;
}
