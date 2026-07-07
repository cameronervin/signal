import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";

export default function DashboardLoading() {
  return (
    <>
      <PageHeader title="Dashboard" subtitle="Loading metrics" />
      <StatePanel title="Loading dashboard" message="Signal is loading queue health and market signals." />
    </>
  );
}
