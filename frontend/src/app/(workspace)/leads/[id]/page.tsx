import { notFound } from "next/navigation";

import { LeadDetailView } from "@/components/features/leads/LeadDetailView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import { createDigitalWorkerAssignmentAction } from "@/app/(workspace)/agents/actions";
import { getDigitalWorkerAssignmentForLead } from "@/lib/api/endpoints/digital-workforce";
import { getLead } from "@/lib/api/endpoints/leads";

interface Props {
  params: Promise<{ id: string }>;
}

export const dynamic = "force-dynamic";

export default async function LeadDetailPage({ params }: Props) {
  const { id } = await params;
  let lead: Awaited<ReturnType<typeof getLead>> | null = null;
  let workerAssignment: Awaited<ReturnType<typeof getDigitalWorkerAssignmentForLead>> | null = null;
  let workerAssignmentUnavailable = false;

  try {
    lead = await getLead(id);
  } catch {
    lead = null;
  }

  if (lead === undefined) {
    notFound();
  }

  if (!lead) {
    return (
      <>
        <PageHeader title="Lead detail" subtitle="API unavailable" />
        <StatePanel
          title="Lead detail unavailable"
          message="Signal could not load this lead from the API. Start the backend or set fixture mode explicitly for local evaluation."
        />
      </>
    );
  }

  if (lead.gates.status === "passed" && lead.draft) {
    try {
      workerAssignment = await getDigitalWorkerAssignmentForLead(lead.id);
    } catch {
      workerAssignmentUnavailable = true;
    }
  }

  return (
    <LeadDetailView
      createAssignmentAction={createDigitalWorkerAssignmentAction}
      lead={lead}
      workerAssignment={workerAssignment ?? undefined}
      workerAssignmentUnavailable={workerAssignmentUnavailable}
    />
  );
}
