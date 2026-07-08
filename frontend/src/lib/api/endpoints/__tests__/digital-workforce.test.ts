import { apiGet, apiPost, isFixtureMode } from "@/lib/api/client";
import { listLeads } from "@/lib/api/endpoints/leads";
import {
  createDigitalWorkerAssignment,
  getDigitalWorkerAssignmentForLead,
  getDigitalWorkerAssignmentDetail,
  listDigitalWorkerHandoffs,
  pauseDigitalWorkerAssignment,
  recordDigitalWorkerInboundEmail,
  resumeDigitalWorkerAssignment
} from "@/lib/api/endpoints/digital-workforce";
import { leads } from "@/lib/fixtures/leads";
import type { DigitalWorkerAssignmentDto } from "@/types/digital-workforce";

jest.mock("@/lib/api/client", () => ({
  apiGet: jest.fn(),
  apiPost: jest.fn(),
  isFixtureMode: jest.fn()
}));

jest.mock("@/lib/api/endpoints/leads", () => ({
  listLeads: jest.fn()
}));

const apiGetMock = jest.mocked(apiGet);
const apiPostMock = jest.mocked(apiPost);
const isFixtureModeMock = jest.mocked(isFixtureMode);
const listLeadsMock = jest.mocked(listLeads);

describe("digital workforce API endpoint mapping", () => {
  beforeEach(() => {
    apiGetMock.mockReset();
    apiPostMock.mockReset();
    isFixtureModeMock.mockReturnValue(false);
    listLeadsMock.mockResolvedValue([leads[0]]);
  });

  it("joins backend assignments to completed lead snapshots for the list view", async () => {
    apiGetMock.mockResolvedValueOnce([backendAssignment()]);

    const rows = await listDigitalWorkerHandoffs();

    expect(apiGetMock).toHaveBeenCalledWith("/api/v1/digital-workforce/assignments");
    expect(rows).toHaveLength(1);
    expect(rows[0]).toMatchObject({
      assignmentId: "31111111-1111-4111-8111-111111111111",
      leadId: leads[0].id,
      status: "active",
      currentPhase: "reply_qualification",
      assignmentStatus: "Active · Reply qualification · Run completed",
      channelReadiness: {
        email: "Sandbox email sent"
      }
    });
  });

  it("prefers active assignment state over terminal history for the same lead", async () => {
    apiGetMock.mockResolvedValueOnce([
      {
        ...backendAssignment(),
        assignment_id: "31111111-2222-4222-8222-111111111111",
        status: "completed",
        created_at: "2026-07-09T16:00:00Z"
      },
      backendAssignment()
    ]);

    const rows = await listDigitalWorkerHandoffs();

    expect(rows[0]).toMatchObject({
      assignmentId: "31111111-1111-4111-8111-111111111111",
      status: "active"
    });
  });

  it("keeps terminal history visible without blocking a new available handoff", async () => {
    apiGetMock.mockResolvedValueOnce([
      {
        ...backendAssignment(),
        status: "completed",
        created_at: "2026-07-09T16:00:00Z"
      }
    ]);

    const rows = await listDigitalWorkerHandoffs();

    expect(rows).toHaveLength(2);
    expect(rows.map((row) => row.status)).toEqual(["available", "completed"]);
  });

  it("returns only active or paused assignments as the current lead assignment", async () => {
    apiGetMock.mockResolvedValueOnce([
      {
        ...backendAssignment(),
        status: "completed"
      }
    ]);

    await expect(getDigitalWorkerAssignmentForLead(leads[0].id)).resolves.toBeUndefined();
  });

  it("returns available handoffs for eligible unassigned leads", async () => {
    apiGetMock.mockResolvedValueOnce([]);

    const rows = await listDigitalWorkerHandoffs();

    expect(rows[0]).toMatchObject({
      leadId: leads[0].id,
      status: "available",
      assignmentStatus: "Ready for assignment"
    });
    expect(rows[0].assignmentId).toBeUndefined();
  });

  it("loads assignment detail by persisted assignment id", async () => {
    apiGetMock.mockResolvedValueOnce(backendAssignment());

    const detail = await getDigitalWorkerAssignmentDetail("31111111-1111-4111-8111-111111111111");

    expect(apiGetMock).toHaveBeenCalledWith(
      "/api/v1/digital-workforce/assignments/31111111-1111-4111-8111-111111111111"
    );
    expect(detail).toMatchObject({
      assignmentId: "31111111-1111-4111-8111-111111111111",
      goals: [{ goal_key: "send_existing_draft" }],
      messages: [{ subject: "Leasing follow-up" }],
      followUps: [{ reason: "first follow-up after initial sandbox email" }],
      runs: [{ status: "completed" }]
    });
  });

  it("returns undefined for missing assignment detail", async () => {
    apiGetMock.mockRejectedValueOnce(new Error("API request failed: 404"));

    await expect(getDigitalWorkerAssignmentDetail("missing")).resolves.toBeUndefined();
  });

  it("posts the backend create assignment contract", async () => {
    const assignment = backendAssignment();
    apiPostMock.mockResolvedValueOnce(assignment);

    await expect(createDigitalWorkerAssignment(leads[0].id)).resolves.toEqual(assignment);

    expect(apiPostMock).toHaveBeenCalledWith("/api/v1/digital-workforce/assignments", {
      lead_id: leads[0].id
    });
  });

  it("keeps create assignment local in fixture mode", async () => {
    isFixtureModeMock.mockReturnValue(true);

    const assignment = await createDigitalWorkerAssignment(leads[0].id);

    expect(apiPostMock).not.toHaveBeenCalled();
    expect(assignment).toMatchObject({
      assignment_id: `worker-preview-${leads[0].id}`,
      lead_id: leads[0].id,
      status: "active"
    });
  });

  it("posts worker transition and inbound email contracts", async () => {
    const assignment = backendAssignment();
    apiPostMock.mockResolvedValue(assignment);

    await pauseDigitalWorkerAssignment(assignment.assignment_id);
    await resumeDigitalWorkerAssignment(assignment.assignment_id);
    await recordDigitalWorkerInboundEmail(assignment.assignment_id, {
      subject: "Re: leasing follow-up",
      body: "Can we schedule a call next week?"
    });

    expect(apiPostMock).toHaveBeenNthCalledWith(
      1,
      "/api/v1/digital-workforce/assignments/31111111-1111-4111-8111-111111111111/pause"
    );
    expect(apiPostMock).toHaveBeenNthCalledWith(
      2,
      "/api/v1/digital-workforce/assignments/31111111-1111-4111-8111-111111111111/resume"
    );
    expect(apiPostMock).toHaveBeenNthCalledWith(
      3,
      "/api/v1/digital-workforce/assignments/31111111-1111-4111-8111-111111111111/inbound-email",
      {
        subject: "Re: leasing follow-up",
        body: "Can we schedule a call next week?"
      }
    );
  });
});

function backendAssignment(): DigitalWorkerAssignmentDto {
  return {
    assignment_id: "31111111-1111-4111-8111-111111111111",
    lead_id: leads[0].id,
    status: "active",
    current_phase: "reply_qualification",
    lifecycle_version: "qualify_to_meeting.v1",
    latest_run_id: "61111111-1111-4111-8111-111111111111",
    activity_log: ["assignment: SDR assigned digital worker", "worker_run: completed"],
    created_at: "2026-07-08T16:00:00Z",
    updated_at: "2026-07-08T16:01:00Z",
    goals: [
      {
        phase_key: "initial_outreach",
        goal_key: "send_existing_draft",
        status: "completed",
        completed_at: "2026-07-08T16:01:00Z",
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
        created_at: "2026-07-08T16:01:00Z"
      }
    ],
    follow_ups: [
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
