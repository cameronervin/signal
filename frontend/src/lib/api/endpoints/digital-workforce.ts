import { apiGet, apiPost, isFixtureMode } from "@/lib/api/client";
import { listLeads } from "@/lib/api/endpoints/leads";
import {
  buildDigitalWorkerAssignmentPreviews,
  digitalWorkerPreviewId,
  getDigitalWorkerAssignmentPreview
} from "@/lib/fixtures/digital-workforce";
import type {
  DigitalWorkerAssignmentCreateDto,
  DigitalWorkerAssignmentDetail,
  DigitalWorkerAssignmentDto,
  DigitalWorkerAssignmentRow,
  DigitalWorkerFollowUpDto,
  DigitalWorkerGoalStateDto,
  DigitalWorkerInboundEmailCreateDto,
  DigitalWorkerMessageDto,
  DigitalWorkerRunDto,
  DigitalWorkerRunStatus,
  DigitalWorkerStepStatus
} from "@/types/digital-workforce";
import type { FixtureLead } from "@/types/lead";

const phaseOrder = [
  "initial_outreach",
  "reply_qualification",
  "objection_or_follow_up",
  "meeting_handoff",
  "closed_outcome"
];

const phaseLabels: Record<string, string> = {
  initial_outreach: "Initial outreach",
  reply_qualification: "Reply qualification",
  objection_or_follow_up: "Objection or follow-up",
  meeting_handoff: "Meeting handoff",
  closed_outcome: "Closed outcome"
};

export async function listDigitalWorkerHandoffs(): Promise<DigitalWorkerAssignmentRow[]> {
  const leads = await listLeads();

  if (isFixtureMode()) {
    return buildDigitalWorkerAssignmentPreviews(leads);
  }

  const assignments = await apiGet<DigitalWorkerAssignmentDto[]>("/api/v1/digital-workforce/assignments");
  return buildDigitalWorkerRows(leads, assignments);
}

export async function getDigitalWorkerAssignmentDetail(
  assignmentId: string
): Promise<DigitalWorkerAssignmentDetail | undefined> {
  if (isFixtureMode()) {
    const leads = await listLeads();
    const fixtureAssignment = getDigitalWorkerAssignmentPreview(assignmentId, leads);
    const lead = fixtureAssignment ? leads.find((item) => item.id === fixtureAssignment.leadId) : undefined;
    return fixtureAssignment
      ? {
          ...fixtureAssignment,
          assignmentId,
          status: "active",
          currentPhase: "initial_outreach",
          lifecycleVersion: "fixture",
          goals: [],
          messages: [],
          followUps: [],
          runs: [],
          draftEmail: lead ? draftEmailForLead(lead) : null
        }
      : undefined;
  }

  try {
    const assignment = await apiGet<DigitalWorkerAssignmentDto>(
      `/api/v1/digital-workforce/assignments/${assignmentId}`
    );
    const lead = await getLeadForAssignment(assignment.lead_id);
    if (!lead) {
      return undefined;
    }
    return mapAssignmentDetail(assignment, lead);
  } catch (error) {
    if (error instanceof Error && error.message.includes("404")) {
      return undefined;
    }
    throw error;
  }
}

export async function getDigitalWorkerAssignmentForLead(
  leadId: string
): Promise<DigitalWorkerAssignmentRow | undefined> {
  const rows = await listDigitalWorkerHandoffs();
  return rows.find((row) => row.leadId === leadId && isBlockingAssignmentStatus(row.status));
}

export async function createDigitalWorkerAssignment(leadId: string): Promise<DigitalWorkerAssignmentDto> {
  if (isFixtureMode()) {
    return fixtureAssignmentDto(leadId);
  }

  return apiPost<DigitalWorkerAssignmentDto, DigitalWorkerAssignmentCreateDto>("/api/v1/digital-workforce/assignments", {
    lead_id: leadId
  });
}

export async function pauseDigitalWorkerAssignment(assignmentId: string): Promise<DigitalWorkerAssignmentDto> {
  if (isFixtureMode()) {
    return fixtureAssignmentDto(leadIdFromFixtureAssignment(assignmentId), {
      assignmentId,
      status: "paused"
    });
  }

  return apiPost<DigitalWorkerAssignmentDto>(`/api/v1/digital-workforce/assignments/${assignmentId}/pause`);
}

export async function resumeDigitalWorkerAssignment(assignmentId: string): Promise<DigitalWorkerAssignmentDto> {
  if (isFixtureMode()) {
    return fixtureAssignmentDto(leadIdFromFixtureAssignment(assignmentId), {
      assignmentId,
      trigger: "manual_resume"
    });
  }

  return apiPost<DigitalWorkerAssignmentDto>(`/api/v1/digital-workforce/assignments/${assignmentId}/resume`);
}

export async function recordDigitalWorkerInboundEmail(
  assignmentId: string,
  payload: DigitalWorkerInboundEmailCreateDto
): Promise<DigitalWorkerAssignmentDto> {
  if (isFixtureMode()) {
    return fixtureAssignmentDto(leadIdFromFixtureAssignment(assignmentId), {
      assignmentId,
      trigger: "inbound_email"
    });
  }

  return apiPost<DigitalWorkerAssignmentDto, DigitalWorkerInboundEmailCreateDto>(
    `/api/v1/digital-workforce/assignments/${assignmentId}/inbound-email`,
    payload
  );
}

export function buildDigitalWorkerRows(
  leads: FixtureLead[],
  assignments: DigitalWorkerAssignmentDto[]
): DigitalWorkerAssignmentRow[] {
  const leadById = new Map(leads.map((lead) => [lead.id, lead]));
  const currentAssignmentByLead = currentAssignmentMapByLead(assignments);
  const rows: DigitalWorkerAssignmentRow[] = leads
    .filter((lead) => isEligibleLead(lead) || currentAssignmentByLead.has(lead.id))
    .map((lead) => {
      const assignment = currentAssignmentByLead.get(lead.id);
      return assignment ? mapAssignedRow(assignment, lead) : mapAvailableRow(lead);
    });
  const terminalRows = assignments
    .filter((assignment) => !isBlockingAssignmentStatus(assignment.status))
    .map((assignment) => {
      const lead = leadById.get(assignment.lead_id);
      return lead ? mapAssignedRow(assignment, lead) : null;
    })
    .filter((row): row is DigitalWorkerAssignmentRow => Boolean(row));

  return [...rows, ...terminalRows].sort(
    (rowA, rowB) => statusSort(rowA) - statusSort(rowB) || rowB.score - rowA.score
  );
}

function mapAvailableRow(lead: FixtureLead): DigitalWorkerAssignmentRow {
  return {
    rowId: `available-${lead.id}`,
    leadId: lead.id,
    leadName: lead.name,
    leadRole: lead.role,
    company: lead.company,
    email: lead.email,
    market: lead.market,
    units: lead.units,
    score: lead.score.total,
    tier: lead.score.tier,
    summary: lead.score.whyLine,
    status: "available",
    marketSignals: lead.marketSignals,
    talkingPoints: lead.talkingPoints,
    assignmentStatus: "Ready for assignment",
    channelReadiness: {
      email: lead.email ? "Ready from lead record" : "Pending contact email",
      text: "Pending contact data",
      humanReview: "Required before worker outreach"
    },
    steps: buildAvailableSteps(),
    activityLog: ["lead: eligible for Digital Worker assignment"]
  };
}

function mapAssignedRow(assignment: DigitalWorkerAssignmentDto, lead: FixtureLead): DigitalWorkerAssignmentRow {
  const latestRun = latestRunForAssignment(assignment.runs, assignment.latest_run_id);

  return {
    rowId: assignment.assignment_id,
    assignmentId: assignment.assignment_id,
    leadId: lead.id,
    leadName: lead.name,
    leadRole: lead.role,
    company: lead.company,
    email: lead.email,
    market: lead.market,
    units: lead.units,
    score: lead.score.total,
    tier: lead.score.tier,
    summary: lead.score.whyLine,
    status: assignment.status,
    currentPhase: assignment.current_phase,
    lifecycleVersion: assignment.lifecycle_version,
    latestRunStatus: latestRun?.status,
    marketSignals: lead.marketSignals,
    talkingPoints: lead.talkingPoints,
    assignmentStatus: assignmentStatusLabel(assignment, latestRun?.status),
    channelReadiness: {
      email: assignment.messages.some((message) => message.direction === "outbound")
        ? "Outreach email sent"
        : "Outreach email queued",
      text: "Pending contact data",
      humanReview: assignment.status === "paused" ? "Paused by SDR" : "SDR check-in available"
    },
    steps: buildAssignmentSteps(assignment),
    activityLog: assignment.activity_log
  };
}

function mapAssignmentDetail(
  assignment: DigitalWorkerAssignmentDto,
  lead: FixtureLead
): DigitalWorkerAssignmentDetail {
  return {
    ...mapAssignedRow(assignment, lead),
    assignmentId: assignment.assignment_id,
    status: assignment.status,
    currentPhase: assignment.current_phase,
    lifecycleVersion: assignment.lifecycle_version,
    goals: assignment.goals,
    messages: assignment.messages,
    followUps: assignment.follow_ups,
    runs: assignment.runs,
    draftEmail: draftEmailForLead(lead)
  };
}

function buildAvailableSteps(): DigitalWorkerAssignmentRow["steps"] {
  return [
    {
      name: "Assignment intake",
      status: "active",
      summary: "Lead context, score, tier, why-line, and draft-ready status are available for handoff.",
      chips: ["Lead context", "Score", "Draft-ready"]
    },
    {
      name: "Initial outreach",
      status: "pending",
      summary: "Assignment will queue the worker and use the existing reviewed draft for outreach.",
      chips: ["Drafted email", "Human gated"]
    },
    {
      name: "Reply qualification",
      status: "pending",
      summary: "Lead replies wake the worker for SDR-visible progress."
    }
  ];
}

function buildAssignmentSteps(assignment: DigitalWorkerAssignmentDto): DigitalWorkerAssignmentRow["steps"] {
  return phaseOrder.map((phaseKey, index) => {
    const phaseGoals = assignment.goals.filter((goal) => goal.phase_key === phaseKey);
    const currentIndex = phaseOrder.indexOf(assignment.current_phase);
    const allGoalsComplete = phaseGoals.length > 0 && phaseGoals.every((goal) => goal.status === "completed");
    const status = stepStatus({
      assignmentStatus: assignment.status,
      currentIndex,
      index,
      allGoalsComplete
    });
    return {
      name: phaseLabels[phaseKey] ?? titleize(phaseKey),
      status,
      summary: stepSummary(phaseKey, phaseGoals, assignment),
      chips: phaseGoals.map((goal) => `${titleize(goal.goal_key)}: ${goal.status}`)
    };
  });
}

function stepStatus({
  assignmentStatus,
  currentIndex,
  index,
  allGoalsComplete
}: {
  assignmentStatus: DigitalWorkerAssignmentDto["status"];
  currentIndex: number;
  index: number;
  allGoalsComplete: boolean;
}): DigitalWorkerStepStatus {
  if (currentIndex > index) {
    return "done";
  }
  if (currentIndex === index) {
    return assignmentStatus === "completed" && allGoalsComplete ? "done" : "active";
  }
  return "pending";
}

function stepSummary(
  phaseKey: string,
  goals: DigitalWorkerGoalStateDto[],
  assignment: DigitalWorkerAssignmentDto
): string {
  const latestCompleted = [...goals].reverse().find((goal) => goal.notes);
  if (latestCompleted?.notes) {
    return latestCompleted.notes;
  }
  if (assignment.current_phase === phaseKey && assignment.status === "paused") {
    return "Assignment is paused; worker communication actions are held.";
  }
  if (assignment.current_phase === phaseKey) {
    return "Current worker phase for this assignment.";
  }
  const pendingGoal = goals.find((goal) => goal.status === "pending");
  return pendingGoal ? `${titleize(pendingGoal.goal_key)} is pending.` : "Worker phase is waiting for progression.";
}

function assignmentStatusLabel(
  assignment: DigitalWorkerAssignmentDto,
  latestRunStatus?: DigitalWorkerRunStatus
): string {
  const phase = phaseLabels[assignment.current_phase] ?? titleize(assignment.current_phase);
  const status = titleize(assignment.status);
  return latestRunStatus ? `${status} · ${phase} · Run ${latestRunStatus}` : `${status} · ${phase}`;
}

function latestRunForAssignment(runs: DigitalWorkerRunDto[], latestRunId?: string | null) {
  return runs.find((run) => run.run_id === latestRunId) ?? runs.at(-1);
}

function currentAssignmentMapByLead(assignments: DigitalWorkerAssignmentDto[]) {
  const sortedAssignments = assignments.filter((assignment) => isBlockingAssignmentStatus(assignment.status)).sort(
    (assignmentA, assignmentB) =>
      assignmentPriority(assignmentA.status) - assignmentPriority(assignmentB.status) ||
      Date.parse(assignmentB.created_at ?? "") - Date.parse(assignmentA.created_at ?? "")
  );
  const assignmentByLead = new Map<string, DigitalWorkerAssignmentDto>();
  for (const assignment of sortedAssignments) {
    if (!assignmentByLead.has(assignment.lead_id)) {
      assignmentByLead.set(assignment.lead_id, assignment);
    }
  }
  return assignmentByLead;
}

function isBlockingAssignmentStatus(status: DigitalWorkerAssignmentRow["status"]) {
  return status === "active" || status === "paused";
}

function assignmentPriority(status: DigitalWorkerAssignmentDto["status"]) {
  const order: Record<DigitalWorkerAssignmentDto["status"], number> = {
    active: 0,
    paused: 1,
    completed: 2,
    failed: 3
  };
  return order[status];
}

async function getLeadForAssignment(leadId: string): Promise<FixtureLead | undefined> {
  const leads = await listLeads();
  return leads.find((lead) => lead.id === leadId);
}

function isEligibleLead(lead: FixtureLead) {
  return lead.gates.status === "passed" && Boolean(lead.draft);
}

function draftEmailForLead(lead: FixtureLead): DigitalWorkerAssignmentDetail["draftEmail"] {
  return lead.draft
    ? {
        id: `lead-draft-${lead.id}`,
        subject: lead.draft.subject,
        body: lead.draft.body,
        sources: lead.draft.sources
      }
    : null;
}

function statusSort(row: DigitalWorkerAssignmentRow) {
  const order: Record<string, number> = {
    active: 0,
    paused: 1,
    available: 2,
    completed: 3,
    failed: 4
  };
  return order[row.status] ?? 5;
}

function titleize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace("Sdr", "SDR");
}

function fixtureAssignmentDto(
  leadId: string,
  options: {
    assignmentId?: string;
    status?: DigitalWorkerAssignmentDto["status"];
    trigger?: DigitalWorkerAssignmentDto["runs"][number]["trigger"];
  } = {}
): DigitalWorkerAssignmentDto {
  const assignmentId = options.assignmentId ?? digitalWorkerPreviewId(leadId);
  const runId = `${assignmentId}-run`;
  return {
    assignment_id: assignmentId,
    lead_id: leadId,
    status: options.status ?? "active",
    current_phase: "initial_outreach",
    lifecycle_version: "fixture",
    latest_run_id: runId,
    activity_log: [
      "fixture: Digital Worker assignment simulated",
      "fixture: no backend state persisted and no outreach email sent"
    ],
    goals: [],
    messages: [],
    follow_ups: [],
    runs: [
      {
        run_id: runId,
        assignment_id: assignmentId,
        trigger: options.trigger ?? "assignment_created",
        status: "queued",
        current_phase: "initial_outreach",
        message: "fixture worker run"
      }
    ]
  };
}

function leadIdFromFixtureAssignment(assignmentId: string) {
  return assignmentId.replace(/^worker-preview-/, "");
}
