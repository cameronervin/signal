import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";

import { LeadDetailView } from "@/components/features/leads/LeadDetailView";
import { getLead } from "@/lib/fixtures/leads";

jest.mock("@xyflow/react", () => ({
  Background: () => null,
  ReactFlow: ({ children }: { children: ReactNode }) => <div data-testid="knowledge-graph">{children}</div>
}));

describe("LeadDetailView", () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined)
      }
    });
  });

  it("renders an editable draft and no live send action for workable leads", () => {
    const lead = getLead("lead-sarah-chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(screen.getByDisplayValue("Improving leasing response in Austin")).toBeInTheDocument();
    expect(screen.getByText("Review gate")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^send$/i })).not.toBeInTheDocument();

    fireEvent.change(screen.getByDisplayValue("Improving leasing response in Austin"), {
      target: { value: "Updated subject" }
    });
    expect(screen.getByDisplayValue("Updated subject")).toBeInTheDocument();
  });

  it("suppresses drafts for gate-failed leads", () => {
    const lead = getLead("lead-tom-whitaker");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(screen.getByText(/Hard gates failed/)).toBeInTheDocument();
    expect(screen.getByText("No draft generated")).toBeInTheDocument();
    expect(screen.queryByText("Drafted email")).not.toBeInTheDocument();
  });
});
