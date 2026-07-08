import { notFound } from "next/navigation";

import { DigitalWorkerProgressView } from "@/components/features/agents/DigitalWorkerProgressView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import { digitalWorkerProfile, getDigitalWorkerAssignmentPreview } from "@/lib/fixtures/digital-workforce";
import { listLeads } from "@/lib/api/endpoints/leads";

interface Props {
  params: Promise<{ runId: string }>;
}

export const dynamic = "force-dynamic";

export default async function DigitalWorkerProgressPage({ params }: Props) {
  const { runId } = await params;
  let assignment: ReturnType<typeof getDigitalWorkerAssignmentPreview> | null = null;

  try {
    assignment = getDigitalWorkerAssignmentPreview(runId, await listLeads());
  } catch {
    assignment = null;
  }

  if (assignment === undefined) {
    notFound();
  }

  if (!assignment) {
    return (
      <>
        <PageHeader title="SDR Digital Worker" subtitle="Lead data unavailable" />
        <StatePanel
          title="Digital worker preview unavailable"
          message="Signal could not load the lead data needed for this preview. Start the backend or set fixture mode explicitly for local evaluation."
          actionLabel="Open Digital Workforce"
          actionHref="/agents"
        />
      </>
    );
  }

  return <DigitalWorkerProgressView assignment={assignment} worker={digitalWorkerProfile} />;
}
