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

const volumeBars = [
  ["chart-h-18", "chart-h-16", "chart-h-10"],
  ["chart-h-20", "chart-h-20", "chart-h-15"],
  ["chart-h-22", "chart-h-24", "chart-h-20"],
  ["chart-h-24", "chart-h-28", "chart-h-25"],
  ["chart-h-26", "chart-h-16", "chart-h-30"],
  ["chart-h-28", "chart-h-20", "chart-h-10"],
  ["chart-h-30", "chart-h-24", "chart-h-15"],
  ["chart-h-32", "chart-h-28", "chart-h-20"],
  ["chart-h-34", "chart-h-16", "chart-h-25"],
  ["chart-h-36", "chart-h-20", "chart-h-30"],
  ["chart-h-38", "chart-h-24", "chart-h-10"],
  ["chart-h-40", "chart-h-28", "chart-h-15"],
  ["chart-h-42", "chart-h-16", "chart-h-20"],
  ["chart-h-44", "chart-h-20", "chart-h-25"]
];

const scoreDistribution = [
  ["chart-h-42", "chart-fill-c"],
  ["chart-h-54", "chart-fill-c"],
  ["chart-h-88", "chart-fill-c"],
  ["chart-h-76", "chart-fill-b"],
  ["chart-h-52", "chart-fill-b"],
  ["chart-h-34", "chart-fill-a"],
  ["chart-h-22", "chart-fill-a"],
  ["chart-h-14", "chart-fill-a"]
];

const markets = [
  ["Austin", "91", "market-score-91", "high"],
  ["Charlotte", "84", "market-score-84", "high"],
  ["Nashville", "79", "market-score-79", "high"],
  ["Phoenix", "73", "market-score-73", "medium"],
  ["Denver", "68", "market-score-68", "medium"],
  ["Seattle", "64", "market-score-64", "medium"]
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
            <span className="sidebar-avatar topbar-avatar" aria-label="SDR profile">
              SD
            </span>
          </div>
        }
      />
      <main className="content stack-lg">
        <section className="kpi-grid">
          {metrics.map((metric) => (
            <MetricCard key={metric.label} {...metric} />
          ))}
        </section>
        <section className="dashboard-chart-grid">
          <div className="surface-card p-5">
            <div className="flex items-center justify-between gap-4">
              <h2 className="section-title">Inbound volume by tier</h2>
              <div className="legend">
                {[
                  ["A", "tier-swatch-a"],
                  ["B", "tier-swatch-b"],
                  ["C", "tier-swatch-c"]
                ].map(([label, swatchClass]) => (
                  <span key={label} className="legend-item">
                    <span className={`legend-swatch ${swatchClass}`} />
                    {label}
                  </span>
                ))}
              </div>
            </div>
            <div className="chart-bars" aria-label="Stacked bar placeholder">
              {volumeBars.map(([tierC, tierB, tierA], index) => (
                <div key={index} className="stacked-bar">
                  <span className={`chart-fill-c ${tierC}`} />
                  <span className={`chart-fill-b ${tierB}`} />
                  <span className={`chart-fill-a ${tierA}`} />
                </div>
              ))}
            </div>
            <div className="chart-axis">
              {["D-13", "D-11", "D-9", "D-7", "D-5", "D-3", "Today"].map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>
          </div>
          <div className="surface-card p-5">
            <div className="flex items-center justify-between gap-4">
              <h2 className="section-title">Score distribution</h2>
              <span className="mono text-soft text-xs font-semibold">187 leads</span>
            </div>
            <div className="chart-bar-grid">
              {scoreDistribution.map(([heightClass, fillClass], index) => (
                <div key={index} className={`chart-bar ${heightClass} ${fillClass}`} />
              ))}
            </div>
            <div className="chart-footer">
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
          <div className="dashboard-market-grid">
            {markets.map(([market, score, scoreClass, toneClass]) => {
              return (
                <div key={market} className="market-bar">
                  <span className="text-sm font-semibold">{market}</span>
                  <span className="meter-track market">
                    <span className={`meter-fill ${toneClass} ${scoreClass}`} />
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
