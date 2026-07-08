import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton, SkeletonText } from "@/components/ui/Skeleton";

export default function DashboardLoading() {
  return (
    <>
      <PageHeader
        title="Dashboard"
        actions={
          <div className="toolbar-row">
            <Skeleton className="h-9 w-32 rounded-lg" />
            <Skeleton className="h-8 w-8 rounded-full" />
          </div>
        }
      />
      <main className="content stack-lg screen-fit dashboard-screen" aria-label="Loading dashboard">
        <section className="grid gap-4 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="metric-card skeleton-card">
              <SkeletonText className="w-24" />
              <Skeleton className="mt-3 h-7 w-16 rounded-md" />
              <SkeletonText className="mt-4 w-32" />
            </div>
          ))}
        </section>
        <section className="dashboard-chart-grid">
          <div className="surface-card chart-card skeleton-card">
            <div className="chart-card-header">
              <SkeletonText className="w-40" />
              <SkeletonText className="w-24" />
            </div>
            <Skeleton className="mt-5 h-[168px] w-full rounded-lg" />
          </div>
          <div className="surface-card chart-card skeleton-card">
            <div className="chart-card-header">
              <SkeletonText className="w-36" />
              <SkeletonText className="w-16" />
            </div>
            <Skeleton className="mt-5 h-[168px] w-full rounded-lg" />
            <div className="mt-4 flex justify-between">
              <SkeletonText className="w-10" />
              <SkeletonText className="w-10" />
              <SkeletonText className="w-10" />
            </div>
          </div>
        </section>
        <section className="surface-card p-5 skeleton-card">
          <div className="flex items-center justify-between gap-4">
            <SkeletonText className="w-48" />
            <SkeletonText className="w-24" />
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="market-bar">
                <span className="market-bar-label">
                  <SkeletonText className="w-24" />
                  <SkeletonText className="w-14" />
                </span>
                <Skeleton className="h-2 w-full rounded-full" />
                <SkeletonText className="w-8" />
              </div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
