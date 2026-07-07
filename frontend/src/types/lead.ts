export type Tier = "A" | "B" | "C";
export type GateStatus = "passed" | "failed";
export type RunStatus = "queued" | "running" | "awaiting_review" | "paused" | "completed" | "failed";
export type AgentStepStatus = "pending" | "running" | "done" | "failed" | "skipped";

export interface SourceFact {
  source: string;
  label: string;
  value: string;
  url?: string | null;
}

export interface FixtureLead {
  id: string;
  name: string;
  email: string;
  role: string;
  company: string;
  market: string;
  units: number | null;
  gates: {
    status: GateStatus;
    failures: string[];
  };
  score: {
    total: number;
    tier: Tier;
    whyLine: string;
  };
  flags: string[];
  talkingPoints: string[];
  marketSignals: Array<{ label: string; value: string }>;
  related: Array<{ label: string; reason: string }>;
  draft: {
    subject: string;
    body: string;
    sources: SourceFact[];
  } | null;
  runId?: string;
}

export interface FixtureAgentRun {
  runId: string;
  leadId?: string;
  agent: string;
  kind: string;
  lead: string;
  started: string;
  stage: string;
  stageIndex: number;
  status: string;
  rawStatus?: RunStatus;
  trigger?: string;
  runtime?: string;
  apisCalled?: string;
  disabled?: boolean;
  steps: Array<{
    name: string;
    status: "done" | "active" | "pending";
    summary: string;
    duration?: string;
    chips?: string[];
  }>;
  activityLog: string[];
  output?: {
    score: number;
    tier: Tier;
    summary: string;
    leadId: string;
  };
}

export interface LeadCreateDto {
  contact_name: string;
  email: string;
  company: string;
  role: string | null;
  property_address: string;
  city: string;
  state: string;
  country: string;
}

export interface GateResultDto {
  status: GateStatus;
  failures: string[];
  warnings: string[];
}

export interface EnrichmentDto {
  market: string;
  coordinates: [number, number] | null;
  renter_share: number | null;
  median_rent: number | null;
  rent_growth_yoy: number | null;
  household_growth: number | null;
  unemployment_rate: number | null;
  company_units: number | null;
  recent_trigger: string | null;
  sources: SourceFact[];
  provider_warnings: string[];
}

export interface ScoreBreakdownDto {
  total: number;
  tier: Tier;
  company_fit: number;
  market_opportunity: number;
  bonuses: number;
  why_line: string;
  components: Record<string, number>;
}

export interface LeadResponseDto {
  id: string;
  input: LeadCreateDto;
  gates: GateResultDto;
  enrichment: EnrichmentDto;
  score: ScoreBreakdownDto;
  talking_points: string[];
  flags: string[];
  draft: {
    subject: string;
    body: string;
    sources: SourceFact[];
  } | null;
  related_leads: Array<{ lead_id: string; label: string; reason: string }>;
  run_id: string;
}

export interface AgentStepDto {
  name: string;
  status: AgentStepStatus;
  summary: string;
  duration_ms: number | null;
}

export interface AgentRunResponseDto {
  run_id: string;
  lead_id: string;
  status: RunStatus;
  trigger: string;
  current_stage: string;
  steps: AgentStepDto[];
  activity_log: string[];
}

export interface AnalyticsSummaryResponseDto {
  total_leads: number;
  tier_distribution: Record<string, number>;
  awaiting_review_count: number;
  gate_failed_count: number;
  average_score: number;
  top_markets: Array<{ market: string; lead_count: number }>;
}

export interface DashboardSummary {
  totalLeads: number;
  tierDistribution: Record<Tier, number>;
  awaitingReviewCount: number;
  gateFailedCount: number;
  averageScore: number;
  topMarkets: Array<{ market: string; leadCount: number; score: number }>;
}
