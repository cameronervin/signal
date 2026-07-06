interface Props {
  label: string;
  value: string;
  detail: string;
  tone?: "positive" | "caution" | "muted";
}

export function MetricCard({ label, value, detail, tone = "positive" }: Props) {
  return (
    <article className="metric-card">
      <span className="metric-label">{label}</span>
      <strong className="metric-value mono">{value}</strong>
      <span className={`metric-detail ${tone}`}>{detail}</span>
    </article>
  );
}
