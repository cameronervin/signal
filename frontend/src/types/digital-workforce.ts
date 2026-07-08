import type { Tier } from "@/types/lead";

export type DigitalWorkerAssignmentStatus = "active" | "paused" | "completed" | "failed";
export type DigitalWorkerRunStatus = "queued" | "running" | "completed" | "failed" | "skipped";
export type DigitalWorkerTrigger = "assignment_created" | "inbound_email" | "follow_up_due" | "manual_resume";
export type DigitalWorkerGoalStatus = "pending" | "completed" | "skipped";
export type DigitalWorkerMessageDirection = "inbound" | "outbound";
export type DigitalWorkerFollowUpStatus = "pending" | "claimed" | "completed" | "cancelled";
export type DigitalWorkerRowStatus = "available" | DigitalWorkerAssignmentStatus;
export type DigitalWorkerStepStatus = "done" | "active" | "pending";

export interface DigitalWorkerCapability {
  label: string;
  detail: string;
  status: "ready" | "preview" | "review";
}

export interface DigitalWorkerProfile {
  workerId: string;
  displayName: string;
  status: string;
  summary: string;
  reviewMode: string;
  capabilities: DigitalWorkerCapability[];
}

export interface DigitalWorkerAssignmentCreateDto {
  lead_id: string;
}

export interface DigitalWorkerInboundEmailCreateDto {
  external_message_id?: string | null;
  received_at?: string | null;
  subject: string;
  body: string;
}

export interface DigitalWorkerGoalStateDto {
  phase_key: string;
  goal_key: string;
  status: DigitalWorkerGoalStatus;
  completed_at?: string | null;
  notes?: string | null;
}

export interface DigitalWorkerMessageDto {
  message_id: string;
  assignment_id: string;
  direction: DigitalWorkerMessageDirection;
  channel: "email";
  subject: string;
  body: string;
  external_message_id?: string | null;
  created_at?: string | null;
}

export interface DigitalWorkerFollowUpDto {
  follow_up_id: string;
  assignment_id: string;
  status: DigitalWorkerFollowUpStatus;
  due_at: string;
  reason: string;
  claimed_run_id?: string | null;
  created_at?: string | null;
}

export interface DigitalWorkerRunDto {
  run_id: string;
  assignment_id: string;
  trigger: DigitalWorkerTrigger;
  status: DigitalWorkerRunStatus;
  current_phase: string;
  message?: string | null;
  created_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  failed_at?: string | null;
}

export interface DigitalWorkerAssignmentDto {
  assignment_id: string;
  lead_id: string;
  status: DigitalWorkerAssignmentStatus;
  current_phase: string;
  lifecycle_version: string;
  latest_run_id?: string | null;
  activity_log: string[];
  created_at?: string | null;
  updated_at?: string | null;
  goals: DigitalWorkerGoalStateDto[];
  messages: DigitalWorkerMessageDto[];
  follow_ups: DigitalWorkerFollowUpDto[];
  runs: DigitalWorkerRunDto[];
}

export interface DigitalWorkerAssignmentRow {
  rowId: string;
  previewId?: string;
  assignmentId?: string;
  leadId: string;
  leadName: string;
  leadRole: string;
  company: string;
  email: string;
  market: string;
  units?: number | null;
  score: number;
  tier: Tier;
  summary: string;
  status: DigitalWorkerRowStatus;
  currentPhase?: string;
  lifecycleVersion?: string;
  latestRunStatus?: DigitalWorkerRunStatus;
  marketSignals: Array<{ label: string; value: string }>;
  talkingPoints: string[];
  assignmentStatus: string;
  channelReadiness: {
    email: string;
    text: string;
    humanReview: string;
  };
  steps: Array<{
    name: string;
    status: DigitalWorkerStepStatus;
    summary: string;
    duration?: string;
    chips?: string[];
  }>;
  activityLog: string[];
}

export interface DigitalWorkerAssignmentDetail extends DigitalWorkerAssignmentRow {
  assignmentId: string;
  status: DigitalWorkerAssignmentStatus;
  currentPhase: string;
  lifecycleVersion: string;
  goals: DigitalWorkerGoalStateDto[];
  messages: DigitalWorkerMessageDto[];
  followUps: DigitalWorkerFollowUpDto[];
  runs: DigitalWorkerRunDto[];
}

export type DigitalWorkerAssignmentPreview = DigitalWorkerAssignmentRow;
