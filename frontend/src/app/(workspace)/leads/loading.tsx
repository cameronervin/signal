import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton, SkeletonText } from "@/components/ui/Skeleton";

export default function LeadsLoading() {
  return (
    <>
      <PageHeader
        title="Inbound Leads"
        subtitle="Loading queue"
        actions={
          <div className="toolbar-row">
            <Skeleton className="h-9 w-24 rounded-lg" />
            <Skeleton className="h-9 w-60 rounded-lg" />
          </div>
        }
      />
      <main className="content stack-lg screen-fit leads-screen" aria-label="Loading inbound leads">
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-8 w-28 rounded-lg" />
          ))}
        </div>
        <section className="surface-card data-table skeleton-card">
          <div className="table-row table-head lead-grid mono">
            <span>Tier</span>
            <span>Lead</span>
            <span>Company</span>
            <span>Market</span>
            <span>Units</span>
            <span>Score</span>
            <span>Why this lead</span>
            <span>Draft</span>
            <span />
          </div>
          <div className="table-body">
            {Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="table-row lead-grid">
                <Skeleton className="h-6 w-14 rounded-lg" />
                <span className="cell-stack">
                  <SkeletonText className="w-28" />
                  <SkeletonText className="w-20" />
                </span>
                <SkeletonText className="w-32" />
                <SkeletonText className="w-24" />
                <SkeletonText className="w-10" />
                <span className="score-meter">
                  <SkeletonText className="w-7" />
                  <Skeleton className="h-2 w-10 rounded-full" />
                </span>
                <span className="grid gap-2">
                  <SkeletonText className="w-full" />
                  <SkeletonText className="w-2/3" />
                </span>
                <Skeleton className="h-8 w-24 rounded-lg" />
                <Skeleton className="h-5 w-5 rounded-md" />
              </div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
