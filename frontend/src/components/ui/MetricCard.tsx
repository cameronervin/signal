interface Props {
  label: string;
  value: string;
  detail: string;
  tone?: "positive" | "caution" | "muted";
}

const toneColor: Record<NonNullable<Props["tone"]>, string> = {
  positive: "var(--brand-deep)",
  caution: "var(--amber-text)",
  muted: "var(--ink-600)"
};

export function MetricCard({ label, value, detail, tone = "positive" }: Props) {
  return (
    <article className="metric-card">
      <span className="block text-xs font-semibold text-[var(--ink-600)]">{label}</span>
      <strong className="mono mt-2 block text-[26px] font-semibold leading-none">{value}</strong>
      <span className="mt-2 block text-[11.5px] font-semibold" style={{ color: toneColor[tone] }}>
        {detail}
      </span>
    </article>
  );
}
