import { ChevronDown } from "lucide-react";

import { DashboardCharts } from "@/components/features/dashboard/DashboardCharts";
import { MetricCard } from "@/components/ui/MetricCard";
import { PageHeader } from "@/components/ui/PageHeader";
import type { DashboardSummary, FixtureLead } from "@/types/lead";

interface Props {
  leads: FixtureLead[];
  summary: DashboardSummary;
}

export function DashboardView({ leads, summary }: Props) {
  const metrics = [
    { label: "Open leads", value: `${summary.totalLeads}`, detail: "Loaded from Signal API", tone: "muted" as const },
    {
      label: "A-tier in queue",
      value: `${summary.tierDistribution.A}`,
      detail: "Touch target under 15m",
      tone: "caution" as const
    },
    {
      label: "Awaiting review",
      value: `${summary.awaitingReviewCount}`,
      detail: "Human gate before outreach",
      tone: "positive" as const
    },
    {
      label: "Gate failed",
      value: `${summary.gateFailedCount}`,
      detail: "No draft exposed",
      tone: "caution" as const
    },
    {
      label: "Average score",
      value: `${Math.round(summary.averageScore)}`,
      detail: "Across open queue",
      tone: "positive" as const
    }
  ];

  return (
    <>
      <PageHeader
        title="Dashboard"
        actions={
          <div className="toolbar-row">
            <button className="button secondary" type="button">
              Last 14 days <ChevronDown size={14} />
            </button>
            <span className="sidebar-avatar m-0" aria-label="SDR profile">
              CE
            </span>
          </div>
        }
      />
      <main className="content stack-lg screen-fit dashboard-screen">
        <section className="grid gap-4 lg:grid-cols-5">
          {metrics.map((metric) => (
            <MetricCard key={metric.label} {...metric} />
          ))}
        </section>
        <DashboardCharts leads={leads} />
        <section className="surface-card p-5">
          <div className="flex items-center justify-between gap-4">
            <h2 className="section-title">Top markets by opportunity</h2>
            <button className="button ghost small" type="button">
              View all markets
            </button>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {summary.topMarkets.map((market) => (
              <div key={market.market} className="market-bar">
                <span className="market-bar-label">
                  <strong>{market.market}</strong>
                  <span>{market.leadCount} leads</span>
                </span>
                <span className="meter-track h-2">
                  <span className={`meter-fill ${market.score >= 75 ? "is-high" : "is-medium"}`} style={{ width: `${market.score}%` }} />
                </span>
                <span className="mono text-sm font-semibold">{market.score}</span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
