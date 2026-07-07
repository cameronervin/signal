import { notFound } from "next/navigation";

import { LeadDetailView } from "@/components/features/leads/LeadDetailView";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";
import { getLead } from "@/lib/api/endpoints/leads";

interface Props {
  params: Promise<{ id: string }>;
}

export const dynamic = "force-dynamic";

export default async function LeadDetailPage({ params }: Props) {
  const { id } = await params;
  let lead: Awaited<ReturnType<typeof getLead>> | null = null;

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

  return <LeadDetailView lead={lead} />;
}
