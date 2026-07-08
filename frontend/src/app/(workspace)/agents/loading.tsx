import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton, SkeletonText } from "@/components/ui/Skeleton";

export default function AgentsLoading() {
  return (
    <>
      <PageHeader
        title="Agent Assignment"
        subtitle="Loading runs"
        actions={
          <div className="toolbar-row">
            <Skeleton className="h-9 w-60 rounded-lg" />
          </div>
        }
      />
      <main className="content stack-lg screen-fit agent-assignment-screen" aria-label="Loading agent assignment">
        <div className="flex flex-wrap gap-2">
          <Skeleton className="h-8 w-28 rounded-lg" />
          <Skeleton className="h-8 w-24 rounded-lg" />
        </div>
        <section className="surface-card data-table skeleton-card">
          <div className="table-row table-head agent-grid mono">
            <span>Agent</span>
            <span>Working lead</span>
            <span>Started</span>
            <span>Stage</span>
            <span>Status</span>
            <span />
          </div>
          <div className="table-body">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="table-row agent-grid">
                <span className="agent-cell">
                  <Skeleton className="h-7 w-7 rounded-lg" />
                  <span className="agent-cell-copy">
                    <SkeletonText className="w-28" />
                    <SkeletonText className="w-20" />
                  </span>
                </span>
                <SkeletonText className="w-40" />
                <SkeletonText className="w-12" />
                <span className="grid gap-2">
                  <SkeletonText className="w-28" />
                  <Skeleton className="h-2 w-full rounded-full" />
                </span>
                <Skeleton className="h-7 w-24 rounded-lg" />
                <Skeleton className="h-5 w-5 rounded-md" />
              </div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
