import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { AgentAssignmentView } from "@/components/features/agents/AgentAssignmentView";
import { AgentRunDetailView } from "@/components/features/agents/AgentRunDetailView";
import { agentRuns } from "@/lib/fixtures/leads";
import { approveAgentRun, pauseAgentRun } from "@/lib/api/endpoints/agent-runs";

jest.mock("@/lib/api/endpoints/agent-runs", () => ({
  approveAgentRun: jest.fn(),
  pauseAgentRun: jest.fn()
}));

describe("Agent views", () => {
  beforeEach(() => {
    jest.mocked(approveAgentRun).mockReset();
    jest.mocked(pauseAgentRun).mockReset();
  });

  it("filters assignment rows and keeps next-release rows disabled", () => {
    render(<AgentAssignmentView agentRuns={agentRuns} />);

    fireEvent.click(screen.getByRole("button", { name: "Awaiting you" }));

    expect(screen.getByText("Sarah Chen · Meridian Residential")).toBeInTheDocument();
    expect(screen.queryByText("Marcus Webb · Northstar Living")).not.toBeInTheDocument();
    expect(screen.queryByText("Auto-cadence outreach")).not.toBeInTheDocument();
  });

  it("pauses and approves through review-gate endpoints", async () => {
    const paused = { ...agentRuns[0], status: "Paused", rawStatus: "paused" as const };
    const approved = { ...agentRuns[0], status: "Completed", rawStatus: "completed" as const };
    jest.mocked(pauseAgentRun).mockResolvedValue(paused);
    jest.mocked(approveAgentRun).mockResolvedValue(approved);

    const { unmount } = render(<AgentRunDetailView run={agentRuns[0]} />);

    fireEvent.click(screen.getAllByRole("button", { name: /^approve review$/i })[0]);
    await waitFor(() => expect(approveAgentRun).toHaveBeenCalledWith(agentRuns[0].runId));
    expect(screen.getByText("Review approved. No outreach was sent.")).toBeInTheDocument();

    unmount();
    render(<AgentRunDetailView run={agentRuns[0]} />);
    fireEvent.click(screen.getByRole("button", { name: /^pause$/i }));
    await waitFor(() => expect(pauseAgentRun).toHaveBeenCalledWith(agentRuns[0].runId));
    expect(screen.getByText("Agent run paused")).toBeInTheDocument();
  });
});
