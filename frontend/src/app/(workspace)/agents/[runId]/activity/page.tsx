import { notFound } from "next/navigation";

import { DigitalWorkerAuditLogView } from "@/components/features/agents/DigitalWorkerAuditLogView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import { getDigitalWorkerAssignmentDetail } from "@/lib/api/endpoints/digital-workforce";
import { routes } from "@/lib/constants/routes";
import { digitalWorkerProfile } from "@/lib/fixtures/digital-workforce";

interface Props {
  params: Promise<{ runId: string }>;
}

export const dynamic = "force-dynamic";

export default async function DigitalWorkerActivityPage({ params }: Props) {
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
        <PageHeader title="Audit Log" subtitle="Lead data unavailable" />
        <StatePanel
          title="Digital worker audit log unavailable"
          message="Signal could not load this Digital Worker assignment. Start the backend or set fixture mode explicitly for local evaluation."
          actionLabel="Open Digital Workforce"
          actionHref={routes.digitalWorkforce}
        />
      </>
    );
  }

  return <DigitalWorkerAuditLogView assignment={assignment} worker={digitalWorkerProfile} />;
}
