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
        <section className="detail-grid digital-worker-detail-grid">
          <div className="surface-card p-5 skeleton-card">
            <SkeletonText className="w-20" />
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="lead-field">
                  <SkeletonText className="w-16" />
                  <Skeleton className="mt-2 h-5 w-32 rounded-md" />
                  <SkeletonText className="mt-2 w-24" />
                </div>
              ))}
            </div>
          </div>
          <section className="surface-card worker-phase-card p-5 skeleton-card">
            <SkeletonText className="w-36" />
            <div className="worker-phase-timeline">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="worker-phase-step">
                  <span className="worker-phase-node">
                    <Skeleton className="h-5 w-5 rounded-full" />
                    {index < 3 && <Skeleton className="h-9 w-0.5 rounded-full" />}
                  </span>
                  <span className="grid gap-2">
                    <SkeletonText className="w-32" />
                    <SkeletonText className="w-full" />
                    <Skeleton className="h-24 w-full rounded-lg" />
                  </span>
                </div>
              ))}
            </div>
          </section>
        </section>
      </main>
    </>
  );
}
