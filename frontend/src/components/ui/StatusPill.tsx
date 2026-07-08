import { cn } from "@/lib/utils/cn";
import type { HTMLAttributes } from "react";

interface Props extends HTMLAttributes<HTMLSpanElement> {
  children: string;
  tone?: "purple" | "warning" | "muted" | "danger";
}

export function StatusPill({ children, className, tone = "purple", ...props }: Props) {
  return (
    <span className={cn("status-pill", tone !== "purple" && tone, className)} {...props}>
      {children}
    </span>
  );
}
