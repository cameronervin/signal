import { notFound } from "next/navigation";

import { AgentRunDetailView } from "@/components/features/agents/AgentRunDetailView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import { getAgentRun } from "@/lib/api/endpoints/agent-runs";

interface Props {
  params: Promise<{ runId: string }>;
}

export const dynamic = "force-dynamic";

export default async function AgentRunPage({ params }: Props) {
  const { runId } = await params;
  let run: Awaited<ReturnType<typeof getAgentRun>> | null = null;

  try {
    run = await getAgentRun(runId);
  } catch {
    run = null;
  }

  if (run === undefined) {
    notFound();
  }

  if (!run) {
    return (
      <>
        <PageHeader title="Agent run" subtitle="API unavailable" />
        <StatePanel
          title="Agent run unavailable"
          message="Signal could not load this run from the API. Start the backend or set fixture mode explicitly for local evaluation."
          actionLabel="Open agents"
          actionHref="/agents"
        />
      </>
    );
  }

  return <AgentRunDetailView run={run} />;
}
