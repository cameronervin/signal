interface Props {
  children: string;
  variant?: "danger" | "warning";
}

export function Flag({ children, variant = "danger" }: Props) {
  return (
    <span className={`flag ${variant === "warning" ? "warning" : ""}`}>
      <span aria-hidden="true">!</span>
      {children}
    </span>
  );
}
