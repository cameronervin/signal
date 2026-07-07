import { cn } from "@/lib/utils/cn";

interface Props {
  children: string;
  tone?: "purple" | "warning" | "muted" | "danger";
}

export function StatusPill({ children, tone = "purple" }: Props) {
  return <span className={cn("status-pill", tone !== "purple" && tone)}>{children}</span>;
}
