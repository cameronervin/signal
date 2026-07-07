import { apiGet, isFixtureMode } from "@/lib/api/client";
import { getLead as getFixtureLead, leads as fixtureLeads } from "@/lib/fixtures/leads";
import type {
  AnalyticsSummaryResponseDto,
  DashboardSummary,
  FixtureLead,
  LeadResponseDto,
  SourceFact,
  Tier
} from "@/types/lead";

const tierOrder: Record<Tier, number> = {
  A: 0,
  B: 1,
  C: 2
};

export async function listLeads(): Promise<FixtureLead[]> {
  if (isFixtureMode()) {
    return sortLeads(fixtureLeads);
  }

  const leads = await apiGet<LeadResponseDto[]>("/api/v1/leads");
  return sortLeads(leads.map(mapLeadResponse));
}

export async function getLead(id: string): Promise<FixtureLead | undefined> {
  if (isFixtureMode()) {
    return getFixtureLead(id);
  }

  try {
    return mapLeadResponse(await apiGet<LeadResponseDto>(`/api/v1/leads/${id}`));
  } catch (error) {
    if (error instanceof Error && error.message.includes("404")) {
      return undefined;
    }
    throw error;
  }
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  if (isFixtureMode()) {
    return summarizeLeads(fixtureLeads);
  }

  const summary = await apiGet<AnalyticsSummaryResponseDto>("/api/v1/analytics/summary");
  return {
    totalLeads: summary.total_leads,
    tierDistribution: normalizeTierDistribution(summary.tier_distribution),
    awaitingReviewCount: summary.awaiting_review_count,
    gateFailedCount: summary.gate_failed_count,
    averageScore: summary.average_score,
    topMarkets: summary.top_markets.map((market, index) => ({
      market: market.market,
      leadCount: market.lead_count,
      score: Math.max(54, 96 - index * 8)
    }))
  };
}

export function sortLeads(leads: FixtureLead[]) {
  return [...leads].sort(
    (leadA, leadB) =>
      tierOrder[leadA.score.tier] - tierOrder[leadB.score.tier] || leadB.score.total - leadA.score.total
  );
}

export function summarizeLeads(leads: FixtureLead[]): DashboardSummary {
  const totalScore = leads.reduce((sum, lead) => sum + lead.score.total, 0);
  const marketCounts = leads.reduce<Record<string, number>>((counts, lead) => {
    counts[lead.market] = (counts[lead.market] ?? 0) + 1;
    return counts;
  }, {});

  return {
    totalLeads: leads.length,
    tierDistribution: normalizeTierDistribution(
      leads.reduce<Record<string, number>>((counts, lead) => {
        counts[lead.score.tier] = (counts[lead.score.tier] ?? 0) + 1;
        return counts;
      }, {})
    ),
    awaitingReviewCount: leads.filter((lead) => lead.gates.status === "passed" && lead.draft).length,
    gateFailedCount: leads.filter((lead) => lead.gates.status === "failed").length,
    averageScore: leads.length ? totalScore / leads.length : 0,
    topMarkets: Object.entries(marketCounts)
      .map(([market, leadCount], index) => ({ market, leadCount, score: Math.max(54, 94 - index * 6) }))
      .sort((a, b) => b.leadCount - a.leadCount || b.score - a.score)
      .slice(0, 6)
  };
}

function normalizeTierDistribution(distribution: Record<string, number>): Record<Tier, number> {
  return {
    A: distribution.A ?? 0,
    B: distribution.B ?? 0,
    C: distribution.C ?? 0
  };
}

function mapLeadResponse(lead: LeadResponseDto): FixtureLead {
  return {
    id: lead.id,
    name: lead.input.contact_name,
    email: lead.input.email,
    role: lead.input.role ?? "Unknown role",
    company: lead.input.company,
    market: lead.enrichment.market || `${lead.input.city}, ${lead.input.state}`,
    units: lead.enrichment.company_units,
    gates: lead.gates,
    score: {
      total: lead.score.total,
      tier: lead.score.tier,
      whyLine: lead.score.why_line
    },
    flags: [...lead.flags, ...lead.gates.failures, ...lead.gates.warnings, ...lead.enrichment.provider_warnings],
    talkingPoints: lead.talking_points,
    marketSignals: buildMarketSignals(lead),
    related: lead.related_leads.map((related) => ({ label: related.label, reason: related.reason })),
    knowledgeGraph: lead.knowledge_graph,
    draft: lead.draft
      ? {
          subject: lead.draft.subject,
          body: lead.draft.body,
          sources: lead.draft.sources
        }
      : null,
    runId: lead.run_id
  };
}

function buildMarketSignals(lead: LeadResponseDto) {
  return [
    { label: "Renter", value: formatPercent(lead.enrichment.renter_share) },
    { label: "Rent YoY", value: formatSignedPercent(lead.enrichment.rent_growth_yoy) },
    { label: "Unemployment", value: formatPercent(lead.enrichment.unemployment_rate) },
    { label: "HH growth", value: formatSignedPercent(lead.enrichment.household_growth) }
  ];
}

function formatPercent(value: number | null) {
  if (value === null) {
    return "n/a";
  }
  return `${Math.round(value * 100)}%`;
}

function formatSignedPercent(value: number | null) {
  if (value === null) {
    return "n/a";
  }
  const percent = value > 1 ? value : value * 100;
  return `${percent >= 0 ? "+" : ""}${percent.toFixed(1)}%`;
}

export function sourceLabel(source: SourceFact) {
  return `${source.source} ${source.label}: ${source.value}`;
}
