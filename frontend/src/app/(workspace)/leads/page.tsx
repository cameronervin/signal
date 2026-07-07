import { InboundLeadsView } from "@/components/features/leads/InboundLeadsView";
import { listLeads } from "@/lib/api/endpoints/leads";

export default async function LeadsPage() {
  const leads = await listLeads();

  return <InboundLeadsView leads={leads} />;
}
