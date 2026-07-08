import { CircleAlert } from "lucide-react";

interface Props {
  children: string;
  variant?: "danger" | "warning";
}

export function Flag({ children, variant = "danger" }: Props) {
  return (
    <span className={`flag ${variant === "warning" ? "warning" : ""}`}>
      <CircleAlert aria-hidden="true" size={13} strokeWidth={2.4} />
      {children}
    </span>
  );
}
