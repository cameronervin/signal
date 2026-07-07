import { AgentAssignmentView } from "@/components/features/agents/AgentAssignmentView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import { listAgentRuns } from "@/lib/api/endpoints/agent-runs";

export const dynamic = "force-dynamic";

export default async function AgentsPage() {
  let agentRuns: Awaited<ReturnType<typeof listAgentRuns>> | null = null;

  try {
    agentRuns = await listAgentRuns();
  } catch {
    agentRuns = null;
  }

  if (!agentRuns) {
    return (
      <>
        <PageHeader title="Agent Assignment" subtitle="API unavailable" />
        <StatePanel
          title="Agent runs unavailable"
          message="Signal could not load agent runs from the API. Start the backend or set fixture mode explicitly for local evaluation."
          actionLabel="Open leads"
          actionHref="/leads"
        />
      </>
    );
  }

  return <AgentAssignmentView agentRuns={agentRuns} />;
}
