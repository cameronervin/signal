import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "primary" | "secondary" | "ghost" | "purple";
  size?: "default" | "small";
}

export function Button({ children, className, variant = "secondary", size = "default", type = "button", ...props }: Props) {
  return (
    <button className={cn("button", variant, size === "small" && "small", className)} type={type} {...props}>
      {children}
    </button>
  );
}
