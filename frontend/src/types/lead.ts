export type Tier = "A" | "B" | "C";
export type GateStatus = "passed" | "failed";
export type RunStatus = "queued" | "running" | "awaiting_review" | "completed" | "failed";
export type StepStatus = "pending" | "running" | "done" | "failed" | "skipped";

export interface SourceFact {
  source: string;
  label: string;
  value: string;
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
}

export interface FixtureAgentRun {
  runId: string;
  agent: string;
  kind: string;
  leadId?: string;
  lead: string;
  started: string;
  stage: string;
  stageIndex: number;
  status: RunStatus;
  statusLabel?: string;
  disabled?: boolean;
  steps: Array<{
    name: string;
    status: StepStatus;
    summary: string;
    duration?: string;
    chips?: string[];
  }>;
  activityLog: string[];
}
