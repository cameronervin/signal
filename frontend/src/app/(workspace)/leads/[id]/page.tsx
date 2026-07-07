import { notFound } from "next/navigation";

import { LeadDetailView } from "@/components/features/leads/LeadDetailView";
import { getLead } from "@/lib/api/endpoints/leads";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function LeadDetailPage({ params }: Props) {
  const { id } = await params;
  const lead = await getLead(id);

  if (!lead) {
    notFound();
  }

  return <LeadDetailView lead={lead} />;
}
