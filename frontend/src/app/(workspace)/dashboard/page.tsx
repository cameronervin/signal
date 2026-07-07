import { DashboardView } from "@/components/features/dashboard/DashboardView";
import { StatePanel } from "@/components/ui/StatePanel";
import { routes } from "@/lib/constants/routes";
import { getDashboardSummary, listLeads } from "@/lib/api/endpoints/leads";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let data: Awaited<ReturnType<typeof loadDashboardData>> | null = null;

  try {
    data = await loadDashboardData();
  } catch {
    data = null;
  }

  if (!data) {
    return (
      <>
        <StatePanel
          title="Dashboard data unavailable"
          message="Signal could not reach the API. Enable fixture mode explicitly or start the backend."
          actionLabel="Open leads"
          actionHref={routes.leads}
        />
      </>
    );
  }

  return <DashboardView leads={data.leads} summary={data.summary} />;
}

async function loadDashboardData() {
  const [leads, summary] = await Promise.all([listLeads(), getDashboardSummary()]);
  return { leads, summary };
}
