import { notFound } from "next/navigation";

import { AgentRunDetailView } from "@/components/features/agents/AgentRunDetailView";
import { getAgentRun } from "@/lib/api/endpoints/agent-runs";

interface Props {
  params: Promise<{ runId: string }>;
}

export default async function AgentRunPage({ params }: Props) {
  const { runId } = await params;
  const run = await getAgentRun(runId);

  if (!run) {
    notFound();
  }

  return <AgentRunDetailView run={run} />;
}
