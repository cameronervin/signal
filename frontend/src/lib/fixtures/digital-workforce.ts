import type { DigitalWorkerAssignmentPreview, DigitalWorkerProfile } from "@/types/digital-workforce";
import type { FixtureLead } from "@/types/lead";

export const digitalWorkerProfile: DigitalWorkerProfile = {
  workerId: "sdr-digital-worker",
  displayName: "SDR Digital Worker",
  status: "Preview only",
  summary:
    "A future SDR teammate that can be assigned to an inbound lead, coordinate email and text follow-up, and keep the human SDR in the review loop.",
  reviewMode: "Human SDR reviews before any outreach leaves Signal.",
  capabilities: [
    {
      label: "Email",
      detail: "Drafts and manages lead email conversations after assignment.",
      status: "ready"
    },
    {
      label: "Text messaging",
      detail: "Prepared as a communication tool; contact data is not stored in this slice.",
      status: "preview"
    },
    {
      label: "Human review",
      detail: "Keeps SDR check-ins and approval gates visible before outreach.",
      status: "review"
    }
  ]
};

export function buildDigitalWorkerAssignmentPreviews(leads: FixtureLead[]): DigitalWorkerAssignmentPreview[] {
  return leads.filter(isEligibleLead).map((lead, index) => buildAssignmentPreview(lead, index));
}

export function digitalWorkerPreviewId(leadId: string) {
  return `worker-preview-${leadId}`;
}

export function getDigitalWorkerAssignmentPreview(
  previewId: string,
  leads: FixtureLead[]
): DigitalWorkerAssignmentPreview | undefined {
  return buildDigitalWorkerAssignmentPreviews(leads).find((preview) => preview.previewId === previewId);
}

function isEligibleLead(lead: FixtureLead) {
  return lead.gates.status === "passed" && Boolean(lead.draft);
}

function buildAssignmentPreview(lead: FixtureLead, index: number): DigitalWorkerAssignmentPreview {
  const activeStep = index % 3;
  const assignmentStatus =
    activeStep === 0 ? "Ready for assignment" : activeStep === 1 ? "Handoff preview" : "SDR check-in preview";

  return {
    rowId: digitalWorkerPreviewId(lead.id),
    previewId: digitalWorkerPreviewId(lead.id),
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
    assignmentStatus,
    channelReadiness: {
      email: lead.email ? "Ready from lead record" : "Pending contact email",
      text: "Pending contact data",
      humanReview: "Required before outreach"
    },
    steps: buildProgressSteps(activeStep),
    activityLog: [
      "preview: inbound lead selected for digital worker handoff",
      "preview: email tool available for reviewed outreach",
      "preview: text messaging tool shown as future capability",
      "preview: no assignment persisted and no outreach sent"
    ]
  };
}

function buildProgressSteps(activeStep: number): DigitalWorkerAssignmentPreview["steps"] {
  const steps: DigitalWorkerAssignmentPreview["steps"] = [
    {
      name: "Assignment intake",
      status: "done",
      summary: "Lead context, score, tier, why-line, and draftable status are available for handoff.",
      chips: ["Lead context", "Score", "Draft-ready"]
    },
    {
      name: "Outreach plan",
      status: activeStep >= 1 ? "done" : "active",
      summary: "Worker prepares the email-first communication plan for SDR review.",
      chips: ["Email first", "SDR owned"]
    },
    {
      name: "Email draft check",
      status: activeStep >= 2 ? "done" : activeStep === 1 ? "active" : "pending",
      summary: "Existing reviewed draft is available as the starting point for worker-managed communication.",
      chips: ["Cited draft", "Editable"]
    },
    {
      name: "Text follow-up readiness",
      status: activeStep === 2 ? "active" : "pending",
      summary: "Text messaging is a future tool and waits for backend contact-data support.",
      chips: ["Future tool", "No phone stored"]
    },
    {
      name: "SDR check-in",
      status: "pending",
      summary: "Human SDR can inspect progress before any communication action is enabled."
    }
  ];

  return steps;
}
