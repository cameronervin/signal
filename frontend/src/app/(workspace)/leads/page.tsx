import { InboundLeadsView } from "@/components/features/leads/InboundLeadsView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import { listLeadQueue } from "@/lib/api/endpoints/leads";

export const dynamic = "force-dynamic";

export default async function LeadsPage() {
  let leads: Awaited<ReturnType<typeof listLeadQueue>> | null = null;

  try {
    leads = await listLeadQueue();
  } catch {
    leads = null;
  }

  if (!leads) {
    return (
      <>
        <PageHeader title="Inbound Leads" subtitle="API unavailable" />
        <StatePanel
          title="Lead queue unavailable"
          message="Signal could not load leads from the API. Start the backend or set fixture mode explicitly for local evaluation."
          actionLabel="Open dashboard"
          actionHref="/dashboard"
        />
      </>
    );
  }

  return <InboundLeadsView leads={leads} />;
}
