import { DigitalWorkforceView } from "@/components/features/agents/DigitalWorkforceView";
import { buildDigitalWorkerAssignmentPreviews } from "@/lib/fixtures/digital-workforce";
import { listLeads } from "@/lib/api/endpoints/leads";

export const dynamic = "force-dynamic";

export default async function DigitalWorkforcePage() {
  let leads: Awaited<ReturnType<typeof listLeads>> = [];
  let leadsUnavailable = false;

  try {
    leads = await listLeads();
  } catch {
    leadsUnavailable = true;
  }

  return (
    <DigitalWorkforceView
      assignments={buildDigitalWorkerAssignmentPreviews(leads)}
      leadsUnavailable={leadsUnavailable}
    />
  );
}
