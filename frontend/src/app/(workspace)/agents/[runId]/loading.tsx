import { ChevronLeft } from "lucide-react";

import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton, SkeletonText } from "@/components/ui/Skeleton";

export default function AgentRunLoading() {
  return (
    <>
      <PageHeader
        title="SDR Digital Worker"
        subtitle="Loading preview"
        actions={
          <div className="toolbar-row">
            <span className="button secondary">
              <ChevronLeft size={16} /> Back
            </span>
            <Skeleton className="h-8 w-28 rounded-lg" />
            <Skeleton className="h-9 w-32 rounded-lg" />
          </div>
        }
      />
      <main className="content stack screen-fit digital-worker-progress-screen" aria-label="Loading digital worker progress">
        <section className="grid gap-3 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="surface-card p-4 skeleton-card">
              <SkeletonText className="w-20" />
              <Skeleton className="mt-2 h-6 w-24 rounded-md" />
            </div>
          ))}
        </section>
        <section className="detail-grid">
          <div className="surface-card p-5 skeleton-card">
            <SkeletonText className="w-20" />
            <div className="mt-5 grid gap-5">
              {Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="stepper-step">
                  <span className="stepper-rail">
                    <Skeleton className="h-5 w-5 rounded-full" />
                  </span>
                  <span className="grid gap-2">
                    <SkeletonText className="w-48" />
                    <SkeletonText className="w-full" />
                    <SkeletonText className="w-3/4" />
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="stack">
            <section className="surface-card p-5 skeleton-card">
              <SkeletonText className="w-24" />
              <Skeleton className="mt-4 h-[220px] w-full rounded-lg" />
            </section>
            <section className="surface-card review-panel p-5 skeleton-card">
              <div className="review-panel-header">
                <SkeletonText className="w-40" />
                <Skeleton className="h-7 w-16 rounded-lg" />
              </div>
              <div className="mt-4 grid gap-2">
                <SkeletonText className="w-full" />
                <SkeletonText className="w-11/12" />
                <SkeletonText className="w-2/3" />
              </div>
              <div className="review-actions">
                <Skeleton className="h-9 w-32 rounded-lg" />
                <Skeleton className="h-9 w-24 rounded-lg" />
                <Skeleton className="h-9 w-24 rounded-lg" />
              </div>
            </section>
          </div>
        </section>
      </main>
    </>
  );
}
