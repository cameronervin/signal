import { cn } from "@/lib/utils/cn";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return <span className={cn("skeleton", className)} aria-hidden="true" />;
}

export function SkeletonText({ className }: SkeletonProps) {
  return <Skeleton className={cn("skeleton-text", className)} />;
}
