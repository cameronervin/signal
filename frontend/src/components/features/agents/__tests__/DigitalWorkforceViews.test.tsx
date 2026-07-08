import { fireEvent, render, screen, within } from "@testing-library/react";

import { DigitalWorkforceView } from "@/components/features/agents/DigitalWorkforceView";
import { DigitalWorkerProgressView } from "@/components/features/agents/DigitalWorkerProgressView";
import { buildDigitalWorkerAssignmentPreviews, digitalWorkerProfile } from "@/lib/fixtures/digital-workforce";
import { leads } from "@/lib/fixtures/leads";
import type { DigitalWorkerAssignmentDetail, DigitalWorkerAssignmentRow } from "@/types/digital-workforce";

jest.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(window.location.search)
}));

describe("Digital Workforce views", () => {
  const createAssignmentAction = jest.fn();
  const pauseAssignmentAction = jest.fn();
  const recordInboundEmailAction = jest.fn();
  const resumeAssignmentAction = jest.fn();
  const availableAssignments = buildDigitalWorkerAssignmentPreviews(leads);
  const assignedAssignment = assignmentDetail();

  beforeEach(() => {
    window.history.replaceState(null, "", "/agents");
    createAssignmentAction.mockReset();
    pauseAssignmentAction.mockReset();
    recordInboundEmailAction.mockReset();
    resumeAssignmentAction.mockReset();
  });

  it("renders available Digital Workforce rows with backend assignment actions", () => {
    render(<DigitalWorkforceView assignments={availableAssignments} createAssignmentAction={createAssignmentAction} />);

    expect(screen.getByRole("heading", { name: "Digital Workforce" })).toBeInTheDocument();
    expect(screen.queryByText("SDR Digital Worker")).not.toBeInTheDocument();
    const assignButtons = screen.getAllByRole("button", { name: /assign/i });
    expect(assignButtons).toHaveLength(5);
    expect(assignButtons[0].closest("form")).toHaveClass("assignment-action-cell");
    expect(screen.queryByText("Agent Assignment")).not.toBeInTheDocument();
    expect(screen.queryByText("Outreach Agent")).not.toBeInTheDocument();
    expect(screen.queryByText("Enrichment Agent")).not.toBeInTheDocument();
  });

  it("links assigned rows to persisted assignment progress", () => {
    render(
      <DigitalWorkforceView
        assignments={[assignedAssignment, ...availableAssignments.slice(1)]}
        createAssignmentAction={createAssignmentAction}
      />
    );

    const tableHead = screen.getByText("Channels").closest(".table-head");
    expect(within(tableHead as HTMLElement).getByText("Tier")).toBeInTheDocument();
    expect(within(tableHead as HTMLElement).getByText("Score")).toBeInTheDocument();
    expect(screen.getByText(assignedAssignment.leadName)).toBeInTheDocument();
    expect(screen.getAllByText(assignedAssignment.tier)[0]).toBeInTheDocument();
    expect(screen.getByText(String(assignedAssignment.score))).toBeInTheDocument();
    expect(screen.queryByText(/ready for a preview handoff/i)).not.toBeInTheDocument();
    expect(
      screen
        .getByText(`${assignedAssignment.leadRole} · ${assignedAssignment.company} · ${assignedAssignment.market}`)
        .closest("a")
    ).toHaveAttribute("href", `/agents/${assignedAssignment.assignmentId}`);
  });

  it("paginates worker-ready handoffs", () => {
    render(<DigitalWorkforceView assignments={availableAssignments} createAssignmentAction={createAssignmentAction} />);

    expect(screen.getByText("Showing 1-5 of 7")).toBeInTheDocument();
    expect(screen.getByText(availableAssignments[0].leadName)).toBeInTheDocument();
    expect(screen.queryByText(availableAssignments[5].leadName)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Next page" }));

    expect(screen.getByText("Showing 6-7 of 7")).toBeInTheDocument();
    expect(screen.getByText(availableAssignments[5].leadName)).toBeInTheDocument();
    expect(screen.queryByText(availableAssignments[0].leadName)).not.toBeInTheDocument();
    expect(window.location.search).toBe("?page=2");
  });

  it("resets pagination when search changes and keeps empty-state copy", () => {
    window.history.replaceState(null, "", "/agents?page=2");
    render(<DigitalWorkforceView assignments={availableAssignments} createAssignmentAction={createAssignmentAction} />);

    expect(screen.getByText(availableAssignments[5].leadName)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Search digital workforce"), {
      target: { value: availableAssignments[0].leadName }
    });

    expect(screen.getByText(availableAssignments[0].leadName)).toBeInTheDocument();
    expect(screen.getByText("Showing 1-1 of 1")).toBeInTheDocument();
    expect(window.location.search).toBe("");

    fireEvent.change(screen.getByLabelText("Search digital workforce"), { target: { value: "does not exist" } });

    expect(screen.getByText("No leads match this search.")).toBeInTheDocument();
    expect(screen.queryByText(/Showing/)).not.toBeInTheDocument();
  });

  it("renders assignment progress from backend worker state", () => {
    render(
      <DigitalWorkerProgressView
        assignment={assignedAssignment}
        pauseAssignmentAction={pauseAssignmentAction}
        recordInboundEmailAction={recordInboundEmailAction}
        resumeAssignmentAction={resumeAssignmentAction}
        worker={digitalWorkerProfile}
      />
    );

    expect(screen.getByRole("heading", { name: "SDR Digital Worker" })).toBeInTheDocument();
    expect(screen.queryByText("Preview only")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /pause/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /record inbound email/i })).toBeInTheDocument();

    const detailColumns = screen.getByText("Lead Information").closest(".detail-grid");
    expect(detailColumns).toBeInTheDocument();
    const headings = within(detailColumns as HTMLElement)
      .getAllByRole("heading")
      .map((heading) => heading.textContent);
    expect(headings).toEqual(["Lead Information", "Helpful context", "Worker activity"]);

    expect(screen.getByText(assignedAssignment.email)).toBeInTheDocument();
    expect(screen.getByText(assignedAssignment.company)).toBeInTheDocument();
    expect(screen.getByText("Initial outreach")).toBeInTheDocument();
    expect(screen.getByText("Reply qualification")).toBeInTheDocument();
    expect(screen.getByText("Sandbox email")).toBeInTheDocument();
    expect(screen.getByText("Leasing follow-up")).toBeInTheDocument();
    expect(screen.getByText("Follow-ups")).toBeInTheDocument();
    expect(screen.getByText("Runs")).toBeInTheDocument();
    expect(screen.getByText("Activity")).toBeInTheDocument();
    expect(screen.queryByText("Check-in log")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve review/i })).not.toBeInTheDocument();
  });
});

function assignmentDetail(): DigitalWorkerAssignmentDetail {
  const base = buildDigitalWorkerAssignmentPreviews(leads)[0] as DigitalWorkerAssignmentRow;
  return {
    ...base,
    rowId: "31111111-1111-4111-8111-111111111111",
    assignmentId: "31111111-1111-4111-8111-111111111111",
    status: "active",
    currentPhase: "reply_qualification",
    lifecycleVersion: "qualify_to_meeting.v1",
    latestRunStatus: "completed",
    assignmentStatus: "Active · Reply qualification · Run completed",
    channelReadiness: {
      email: "Sandbox email sent",
      text: "Pending contact data",
      humanReview: "SDR check-in available"
    },
    steps: [
      {
        name: "Initial outreach",
        status: "done",
        summary: "Existing lead-intelligence draft sent through sandbox email."
      },
      {
        name: "Reply qualification",
        status: "active",
        summary: "Current worker phase for this sandbox assignment."
      }
    ],
    activityLog: ["assignment: SDR assigned digital worker", "worker_run: completed"],
    goals: [
      {
        phase_key: "initial_outreach",
        goal_key: "send_existing_draft",
        status: "completed",
        notes: "Existing lead-intelligence draft sent through sandbox email."
      }
    ],
    messages: [
      {
        message_id: "41111111-1111-4111-8111-111111111111",
        assignment_id: "31111111-1111-4111-8111-111111111111",
        direction: "outbound",
        channel: "email",
        subject: "Leasing follow-up",
        body: "Sandbox email body",
        created_at: "2026-07-08T16:00:00Z"
      }
    ],
    followUps: [
      {
        follow_up_id: "51111111-1111-4111-8111-111111111111",
        assignment_id: "31111111-1111-4111-8111-111111111111",
        status: "pending",
        due_at: "2026-07-09T16:00:00Z",
        reason: "first follow-up after initial sandbox email"
      }
    ],
    runs: [
      {
        run_id: "61111111-1111-4111-8111-111111111111",
        assignment_id: "31111111-1111-4111-8111-111111111111",
        trigger: "assignment_created",
        status: "completed",
        current_phase: "reply_qualification",
        message: "digital worker completed one wake-up",
        created_at: "2026-07-08T16:00:00Z"
      }
    ]
  };
}
