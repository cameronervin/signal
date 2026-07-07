import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";

export default function LeadsLoading() {
  return (
    <>
      <PageHeader title="Inbound Leads" subtitle="Loading queue" />
      <StatePanel title="Loading leads" message="Signal is loading the ranked queue." />
    </>
  );
}
