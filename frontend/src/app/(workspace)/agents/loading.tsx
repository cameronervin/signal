import { PageHeader } from "@/components/ui/PageHeader";
import { StatePanel } from "@/components/ui/StatePanel";

export default function AgentsLoading() {
  return (
    <>
      <PageHeader title="Agent Assignment" subtitle="Loading runs" />
      <StatePanel title="Loading agent runs" message="Signal is loading the current agent work queue." />
    </>
  );
}
