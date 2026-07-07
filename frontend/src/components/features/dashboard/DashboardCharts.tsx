"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { FixtureLead, Tier } from "@/types/lead";

interface Props {
  leads: FixtureLead[];
}

const tierKeys: Tier[] = ["C", "B", "A"];

export function DashboardCharts({ leads }: Props) {
  const volume = buildVolumeData(leads);
  const distribution = buildDistributionData(leads);

  return (
    <section className="dashboard-chart-grid">
      <div className="surface-card chart-card">
        <div className="chart-card-header">
          <h2 className="section-title">Inbound volume by tier</h2>
          <div className="chart-legend">
            {["A", "B", "C"].map((tier) => (
              <span key={tier}>
                <span className={`legend-dot tier-${tier.toLowerCase()}`} />
                {tier}
              </span>
            ))}
          </div>
        </div>
        <div className="chart-frame" aria-label="Inbound volume by tier chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={volume}>
              <XAxis dataKey="label" tickLine={false} axisLine={false} />
              <YAxis hide />
              <Tooltip cursor={false} />
              {tierKeys.map((tier) => (
                <Bar key={tier} dataKey={tier} stackId="tier" fill={`var(--tier-${tier.toLowerCase()})`} radius={4} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="surface-card chart-card">
        <div className="chart-card-header">
          <h2 className="section-title">Score distribution</h2>
          <span className="mono chart-meta">{leads.length} leads</span>
        </div>
        <div className="chart-frame" aria-label="Score distribution chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={distribution}>
              <XAxis dataKey="bucket" tickLine={false} axisLine={false} />
              <YAxis hide />
              <Tooltip cursor={false} />
              <Bar dataKey="count" fill="var(--brand-primary)" radius={4} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-footer">
          <span>C {percentage(leads, "C")}</span>
          <span>B {percentage(leads, "B")}</span>
          <span>A {percentage(leads, "A")}</span>
        </div>
      </div>
    </section>
  );
}

function buildVolumeData(leads: FixtureLead[]) {
  return Array.from({ length: 14 }).map((_, index) => {
    const windowLeads = leads.filter((_, leadIndex) => (leadIndex + index) % 3 !== 0);
    return {
      label: index === 13 ? "Today" : `D-${13 - index}`,
      A: Math.max(0, windowLeads.filter((lead) => lead.score.tier === "A").length + (index % 2)),
      B: Math.max(0, windowLeads.filter((lead) => lead.score.tier === "B").length + (index % 3)),
      C: Math.max(0, windowLeads.filter((lead) => lead.score.tier === "C").length + (index % 2))
    };
  });
}

function buildDistributionData(leads: FixtureLead[]) {
  const buckets = [
    { bucket: "0-39", count: 0 },
    { bucket: "40-49", count: 0 },
    { bucket: "50-59", count: 0 },
    { bucket: "60-69", count: 0 },
    { bucket: "70-79", count: 0 },
    { bucket: "80-89", count: 0 },
    { bucket: "90+", count: 0 }
  ];

  leads.forEach((lead) => {
    const score = lead.score.total;
    const index = score >= 90 ? 6 : score >= 80 ? 5 : score >= 70 ? 4 : score >= 60 ? 3 : score >= 50 ? 2 : score >= 40 ? 1 : 0;
    buckets[index].count += 1;
  });

  return buckets;
}

function percentage(leads: FixtureLead[], tier: Tier) {
  if (!leads.length) {
    return "0%";
  }
  return `${Math.round((leads.filter((lead) => lead.score.tier === tier).length / leads.length) * 100)}%`;
}
