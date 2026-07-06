import { ChevronDown } from "lucide-react";

import { MetricCard } from "@/components/ui/MetricCard";
import { PageHeader } from "@/components/ui/PageHeader";

const metrics = [
  { label: "New leads today", value: "42", detail: "+8 vs yesterday", tone: "positive" as const },
  { label: "A-tier in queue", value: "11", detail: "Touch target under 15m", tone: "caution" as const },
  { label: "Median speed-to-lead", value: "14m", detail: "Down from 41m baseline", tone: "positive" as const },
  { label: "Drafts approved 7d", value: "128", detail: "Avg 4 edits per draft", tone: "muted" as const },
  { label: "First-touch response", value: "34%", detail: "+6 pts", tone: "positive" as const }
];

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Dashboard"
        actions={
          <div className="flex items-center gap-3">
            <button className="button secondary" type="button">
              Last 14 days <ChevronDown size={14} />
            </button>
            <span className="sidebar-avatar m-0" aria-label="SDR profile">
              SD
            </span>
          </div>
        }
      />
      <main className="content stack-lg">
        <section className="grid gap-4 lg:grid-cols-5">
          {metrics.map((metric) => (
            <MetricCard key={metric.label} {...metric} />
          ))}
        </section>
        <section className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
          <div className="surface-card p-5">
            <div className="flex items-center justify-between gap-4">
              <h2 className="section-title">Inbound volume by tier</h2>
              <div className="flex gap-4 text-[11px] font-semibold text-[var(--ink-600)]">
                {[
                  ["A", "var(--tier-a)"],
                  ["B", "var(--tier-b)"],
                  ["C", "var(--tier-c)"]
                ].map(([label, color]) => (
                  <span key={label} className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-sm" style={{ background: color }} />
                    {label}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-5 flex h-52 items-end gap-3" aria-label="Stacked bar placeholder">
              {Array.from({ length: 14 }).map((_, index) => (
                <div key={index} className="flex flex-1 flex-col overflow-hidden rounded-md bg-[var(--track)]">
                  <span style={{ height: `${18 + index * 2}%` }} className="bg-[var(--tier-c)]" />
                  <span style={{ height: `${16 + (index % 4) * 4}%` }} className="bg-[var(--tier-b)]" />
                  <span style={{ height: `${10 + (index % 5) * 5}%` }} className="bg-[var(--tier-a)]" />
                </div>
              ))}
            </div>
            <div className="mono mt-3 grid grid-cols-7 text-[10px] text-[var(--ink-400)]">
              {["D-13", "D-11", "D-9", "D-7", "D-5", "D-3", "Today"].map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>
          </div>
          <div className="surface-card p-5">
            <div className="flex items-center justify-between gap-4">
              <h2 className="section-title">Score distribution</h2>
              <span className="mono text-[11px] font-semibold text-[var(--ink-400)]">187 leads</span>
            </div>
            <div className="mt-5 grid h-52 grid-cols-8 items-end gap-2">
              {[42, 54, 88, 76, 52, 34, 22, 14].map((height, index) => (
                <div
                  key={index}
                  className="rounded-md"
                  style={{
                    background:
                      index > 4 ? "var(--tier-a)" : index > 2 ? "var(--tier-b)" : "var(--tier-c)",
                    height: `${height}%`
                  }}
                />
              ))}
            </div>
            <div className="mt-4 flex justify-between text-xs font-semibold text-[var(--ink-600)]">
              <span>C 61%</span>
              <span>B 24%</span>
              <span>A 15%</span>
            </div>
          </div>
        </section>
        <section className="surface-card p-5">
          <div className="flex items-center justify-between gap-4">
            <h2 className="section-title">Top markets by opportunity</h2>
            <button className="button ghost small" type="button">
              View all markets
            </button>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {["Austin", "Charlotte", "Nashville", "Phoenix", "Denver", "Seattle"].map((market, index) => {
              const score = [91, 84, 79, 73, 68, 64][index];
              return (
                <div key={market} className="market-bar">
                  <span className="text-sm font-semibold">{market}</span>
                  <span className="meter-track h-2">
                    <span
                      className="meter-fill"
                      style={{ background: score >= 75 ? "var(--brand-primary)" : "var(--tier-b)", width: `${score}%` }}
                    />
                  </span>
                  <span className="mono text-sm font-semibold">{score}</span>
                </div>
              );
            })}
          </div>
        </section>
      </main>
    </>
  );
}
