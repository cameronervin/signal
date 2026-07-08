import { ChevronLeft } from "lucide-react";

import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton, SkeletonText } from "@/components/ui/Skeleton";

export default function LeadDetailLoading() {
  return (
    <>
      <PageHeader
        title="Lead detail"
        subtitle="Loading enrichment"
        actions={
          <div className="flex gap-2">
            <span className="button secondary">
              <ChevronLeft size={16} /> Back
            </span>
            <Skeleton className="h-9 w-32 rounded-lg" />
          </div>
        }
      />
      <main className="content stack" aria-label="Loading lead detail">
        <div className="score-summary">
          <Skeleton className="h-6 w-16 rounded-lg" />
          <SkeletonText className="w-10" />
          <SkeletonText className="w-80 max-w-full" />
        </div>
        <section className="detail-grid">
          <div className="stack">
            <section className="surface-card p-5 skeleton-card">
              <SkeletonText className="w-36" />
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={index} className="lead-field">
                    <SkeletonText className="w-16" />
                    <SkeletonText className="mt-2 w-36" />
                    <SkeletonText className="mt-2 w-44" />
                  </div>
                ))}
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3 border-t border-[var(--border)] pt-5 sm:grid-cols-4">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={index}>
                    <SkeletonText className="w-16" />
                    <Skeleton className="mt-2 h-6 w-14 rounded-md" />
                  </div>
                ))}
              </div>
            </section>
            <section className="surface-card p-5 skeleton-card">
              <SkeletonText className="w-28" />
              <div className="mt-4 grid gap-3">
                <SkeletonText className="w-full" />
                <SkeletonText className="w-11/12" />
                <SkeletonText className="w-10/12" />
              </div>
            </section>
            <section className="surface-card p-5 skeleton-card">
              <div className="flex items-center justify-between gap-4">
                <SkeletonText className="w-32" />
                <Skeleton className="h-7 w-20 rounded-lg" />
              </div>
              <Skeleton className="mt-4 h-[230px] w-full rounded-lg" />
            </section>
          </div>
          <section className="surface-card flex flex-col p-5 skeleton-card">
            <div className="flex items-center justify-between gap-3">
              <SkeletonText className="w-32" />
              <Skeleton className="h-7 w-24 rounded-lg" />
            </div>
            <div className="mt-4 grid gap-2 border-b border-[var(--border)] pb-4">
              <SkeletonText className="w-44" />
              <SkeletonText className="w-52" />
            </div>
            <div className="mt-4 grid gap-4">
              <SkeletonText className="w-16" />
              <Skeleton className="h-11 w-full rounded-lg" />
              <SkeletonText className="w-12" />
              <Skeleton className="h-[260px] w-full rounded-lg" />
            </div>
            <Skeleton className="mt-4 h-11 w-full rounded-lg" />
            <div className="mt-auto flex justify-between pt-5">
              <Skeleton className="h-9 w-28 rounded-lg" />
              <div className="flex gap-2">
                <Skeleton className="h-9 w-20 rounded-lg" />
                <Skeleton className="h-9 w-32 rounded-lg" />
              </div>
            </div>
          </section>
        </section>
      </main>
    </>
  );
}
