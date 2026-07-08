import { DigitalWorkforceView } from "@/components/features/agents/DigitalWorkforceView";
import { createDigitalWorkerAssignmentAction } from "@/app/(workspace)/agents/actions";
import { listDigitalWorkerHandoffs } from "@/lib/api/endpoints/digital-workforce";

export const dynamic = "force-dynamic";

export default async function DigitalWorkforcePage() {
  let assignments: Awaited<ReturnType<typeof listDigitalWorkerHandoffs>> = [];
  let dataUnavailable = false;

  try {
    assignments = await listDigitalWorkerHandoffs();
  } catch {
    dataUnavailable = true;
  }

  return (
    <DigitalWorkforceView
      assignments={assignments}
      createAssignmentAction={createDigitalWorkerAssignmentAction}
      dataUnavailable={dataUnavailable}
    />
  );
}
