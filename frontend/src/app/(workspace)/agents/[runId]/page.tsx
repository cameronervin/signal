import { notFound } from "next/navigation";

import { DigitalWorkerProgressView } from "@/components/features/agents/DigitalWorkerProgressView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import {
  pauseDigitalWorkerAssignmentAction,
  recordDigitalWorkerInboundEmailAction,
  resumeDigitalWorkerAssignmentAction
} from "@/app/(workspace)/agents/actions";
import { getDigitalWorkerAssignmentDetail } from "@/lib/api/endpoints/digital-workforce";
import { digitalWorkerProfile } from "@/lib/fixtures/digital-workforce";

interface Props {
  params: Promise<{ runId: string }>;
}

export const dynamic = "force-dynamic";

export default async function DigitalWorkerProgressPage({ params }: Props) {
  const { runId: assignmentId } = await params;
  let assignment: Awaited<ReturnType<typeof getDigitalWorkerAssignmentDetail>> | null = null;

  try {
    assignment = await getDigitalWorkerAssignmentDetail(assignmentId);
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
          title="Digital worker assignment unavailable"
          message="Signal could not load this Digital Worker assignment. Start the backend or set fixture mode explicitly for local evaluation."
          actionLabel="Open Digital Workforce"
          actionHref="/agents"
        />
      </>
    );
  }

  return (
    <DigitalWorkerProgressView
      assignment={assignment}
      pauseAssignmentAction={pauseDigitalWorkerAssignmentAction}
      recordInboundEmailAction={recordDigitalWorkerInboundEmailAction}
      resumeAssignmentAction={resumeDigitalWorkerAssignmentAction}
      worker={digitalWorkerProfile}
    />
  );
}
