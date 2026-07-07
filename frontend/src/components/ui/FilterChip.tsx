import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  active?: boolean;
}

export function FilterChip({ children, active = false, className, type = "button", ...props }: Props) {
  return (
    <button className={cn("filter-chip", active && "active", className)} type={type} {...props}>
      {children}
    </button>
  );
}
