import { apiGet, apiPost, isFixtureMode } from "@/lib/api/client";
import { agentRuns as fixtureAgentRuns, getAgentRun as getFixtureAgentRun } from "@/lib/fixtures/leads";
import { listLeads } from "@/lib/api/endpoints/leads";
import type { AgentRunResponseDto, FixtureAgentRun, FixtureLead, RunStatus } from "@/types/lead";

export async function listAgentRuns(): Promise<FixtureAgentRun[]> {
  if (isFixtureMode()) {
    return fixtureAgentRuns;
  }

  const [runs, leads] = await Promise.all([apiGet<AgentRunResponseDto[]>("/api/v1/agent-runs"), listLeads()]);
  return runs.map((run) => mapAgentRunResponse(run, leads.find((lead) => lead.id === run.lead_id)));
}

export async function getAgentRun(runId: string): Promise<FixtureAgentRun | undefined> {
  if (isFixtureMode()) {
    return getFixtureAgentRun(runId);
  }

  try {
    const [run, leads] = await Promise.all([apiGet<AgentRunResponseDto>(`/api/v1/agent-runs/${runId}`), listLeads()]);
    return mapAgentRunResponse(run, leads.find((lead) => lead.id === run.lead_id));
  } catch (error) {
    if (error instanceof Error && error.message.includes("404")) {
      return undefined;
    }
    throw error;
  }
}

export async function approveAgentRun(runId: string): Promise<FixtureAgentRun> {
  if (isFixtureMode()) {
    return updateFixtureRun(runId, "completed", "review_approved", "human_review: approved without send");
  }

  const [run, leads] = await Promise.all([
    apiPost<AgentRunResponseDto>(`/api/v1/agent-runs/${runId}/approve`),
    listLeads()
  ]);
  return mapAgentRunResponse(run, leads.find((lead) => lead.id === run.lead_id));
}

export async function pauseAgentRun(runId: string): Promise<FixtureAgentRun> {
  if (isFixtureMode()) {
    return updateFixtureRun(runId, "paused", "human_review_paused", "agent_run: paused");
  }

  const [run, leads] = await Promise.all([
    apiPost<AgentRunResponseDto>(`/api/v1/agent-runs/${runId}/pause`),
    listLeads()
  ]);
  return mapAgentRunResponse(run, leads.find((lead) => lead.id === run.lead_id));
}

function updateFixtureRun(runId: string, status: RunStatus, stage: string, activity: string): FixtureAgentRun {
  const run = getFixtureAgentRun(runId);

  if (!run) {
    throw new Error("Agent run not found");
  }

  return {
    ...run,
    rawStatus: status,
    status: statusLabel(status),
    stage: stageLabel(stage),
    activityLog: [...run.activityLog, activity],
    steps: run.steps.map((step) =>
      step.name === "Human review" ? { ...step, status: status === "paused" ? "active" : "done" } : step
    )
  };
}

function mapAgentRunResponse(run: AgentRunResponseDto, lead?: FixtureLead): FixtureAgentRun {
  const totalDurationMs = run.steps.reduce((sum, step) => sum + (step.duration_ms ?? 0), 0);
  const doneSteps = run.steps.filter((step) => step.status === "done" || step.status === "skipped").length;
  const output = lead
    ? {
        score: lead.score.total,
        tier: lead.score.tier,
        summary: lead.score.whyLine,
        leadId: lead.id
      }
    : undefined;

  return {
    runId: run.run_id,
    leadId: run.lead_id,
    agent: run.current_stage.includes("enrich") ? "Enrichment Agent" : "Outreach Agent",
    kind: run.trigger.replaceAll("_", " "),
    lead: lead ? `${lead.name} · ${lead.company}` : run.lead_id,
    started: "Live",
    stage: stageLabel(run.current_stage),
    stageIndex: Math.max(1, doneSteps),
    status: statusLabel(run.status),
    rawStatus: run.status,
    trigger: run.trigger.replaceAll("_", " "),
    runtime: totalDurationMs ? `${(totalDurationMs / 1000).toFixed(1)}s` : "n/a",
    apisCalled: apiCallSummary(run.activity_log),
    steps: run.steps.map((step) => ({
      name: displayStepName(step.name),
      status: stepStatus(step.status, run.current_stage, step.name),
      summary: displayStepSummary(step.name, step.summary),
      duration: step.duration_ms ? `${(step.duration_ms / 1000).toFixed(1)}s` : undefined
    })),
    activityLog: run.activity_log,
    output
  };
}

function displayStepName(name: string) {
  return name.toLowerCase() === "send" ? "Complete" : name;
}

function displayStepSummary(name: string, summary: string) {
  return name.toLowerCase() === "send" ? "Review completion is logged. No outreach is sent by Signal v1." : summary;
}

function stageLabel(stage: string) {
  return stage
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace("Human Review", "Human review")
    .replace("Review Approved", "Review approved");
}

function statusLabel(status: RunStatus) {
  const labels: Record<RunStatus, string> = {
    queued: "Queued",
    running: "In progress",
    awaiting_review: "Awaiting you",
    paused: "Paused",
    completed: "Completed",
    failed: "Failed"
  };

  return labels[status];
}

function stepStatus(status: AgentRunResponseDto["steps"][number]["status"], currentStage: string, name: string) {
  if (status === "done" || status === "skipped") {
    return "done";
  }
  if (status === "running" || currentStage.toLowerCase().includes(name.toLowerCase().split(" ")[0])) {
    return "active";
  }
  if (status === "failed") {
    return "active";
  }
  return "pending";
}

function apiCallSummary(activityLog: string[]) {
  const resolved = activityLog.filter((entry) => entry.includes("resolved") || entry.includes("completed")).length;
  return resolved ? `${resolved} resolved` : "n/a";
}
