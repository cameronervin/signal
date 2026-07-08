import type { Tier } from "@/types/lead";

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

export interface DigitalWorkerAssignmentPreview {
  previewId: string;
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
    status: "done" | "active" | "pending";
    summary: string;
    duration?: string;
    chips?: string[];
  }>;
  activityLog: string[];
}
