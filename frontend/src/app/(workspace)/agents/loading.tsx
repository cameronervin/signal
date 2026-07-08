import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton, SkeletonText } from "@/components/ui/Skeleton";

export default function AgentsLoading() {
  return (
    <>
      <PageHeader
        title="Digital Workforce"
        subtitle="Loading eligible leads"
        actions={
          <div className="toolbar-row">
            <Skeleton className="h-9 w-60 rounded-lg" />
          </div>
        }
      />
      <main className="content stack-lg screen-fit digital-workforce-screen" aria-label="Loading digital workforce">
        <section className="surface-card data-table skeleton-card">
          <div className="table-row table-head digital-workforce-grid mono">
            <span>Tier</span>
            <span>Lead</span>
            <span>Score</span>
            <span>Channels</span>
            <span>Assignment preview</span>
            <span />
          </div>
          <div className="table-body">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="table-row digital-workforce-grid">
                <Skeleton className="h-6 w-14 rounded-lg" />
                <span className="grid gap-2">
                  <SkeletonText className="w-40" />
                  <SkeletonText className="w-56" />
                </span>
                <span className="grid gap-2">
                  <Skeleton className="h-2 w-28 rounded-full" />
                </span>
                <SkeletonText className="w-44" />
                <SkeletonText className="w-full" />
                <Skeleton className="h-5 w-5 rounded-md" />
              </div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
