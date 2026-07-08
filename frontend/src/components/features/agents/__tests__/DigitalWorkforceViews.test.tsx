import { fireEvent, render, screen, within } from "@testing-library/react";

import { DigitalWorkforceView } from "@/components/features/agents/DigitalWorkforceView";
import { DigitalWorkerProgressView } from "@/components/features/agents/DigitalWorkerProgressView";
import { buildDigitalWorkerAssignmentPreviews, digitalWorkerProfile } from "@/lib/fixtures/digital-workforce";
import { leads } from "@/lib/fixtures/leads";

jest.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(window.location.search)
}));

describe("Digital Workforce views", () => {
  const assignments = buildDigitalWorkerAssignmentPreviews(leads);

  beforeEach(() => {
    window.history.replaceState(null, "", "/agents");
  });

  it("renders the Digital Workforce table without the worker profile or filter chips", () => {
    render(<DigitalWorkforceView assignments={assignments} />);

    expect(screen.getByRole("heading", { name: "Digital Workforce" })).toBeInTheDocument();
    expect(screen.queryByText("SDR Digital Worker")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /eligible leads/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /text pending/i })).not.toBeInTheDocument();
    expect(screen.queryByText("Agent Assignment")).not.toBeInTheDocument();
    expect(screen.queryByText("Outreach Agent")).not.toBeInTheDocument();
    expect(screen.queryByText("Enrichment Agent")).not.toBeInTheDocument();
  });

  it("shows eligible leads as clickable rows with chevron-style navigation", () => {
    render(<DigitalWorkforceView assignments={assignments} />);

    const tableHead = screen.getByText("Channels").closest(".table-head");
    expect(within(tableHead as HTMLElement).getByText("Tier")).toBeInTheDocument();
    expect(within(tableHead as HTMLElement).getByText("Score")).toBeInTheDocument();
    expect(screen.getByText(assignments[0].leadName)).toBeInTheDocument();
    expect(screen.getAllByText(assignments[0].tier)[0]).toBeInTheDocument();
    expect(screen.getByText(String(assignments[0].score))).toBeInTheDocument();
    expect(screen.queryByText(/ready for a preview handoff/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^assign/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/^Preview$/)).not.toBeInTheDocument();
    expect(
      screen.getByText(`${assignments[0].leadRole} · ${assignments[0].company} · ${assignments[0].market}`).closest("a")
    ).toHaveAttribute("href", `/agents/${assignments[0].previewId}`);
  });

  it("paginates eligible assignment handoffs", () => {
    render(<DigitalWorkforceView assignments={assignments} />);

    expect(screen.getByText("Showing 1-5 of 7")).toBeInTheDocument();
    expect(screen.getByText(assignments[0].leadName)).toBeInTheDocument();
    expect(screen.queryByText(assignments[5].leadName)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Next page" }));

    expect(screen.getByText("Showing 6-7 of 7")).toBeInTheDocument();
    expect(screen.getByText(assignments[5].leadName)).toBeInTheDocument();
    expect(screen.queryByText(assignments[0].leadName)).not.toBeInTheDocument();
    expect(window.location.search).toBe("?page=2");
  });

  it("resets pagination when search changes and keeps empty-state copy", () => {
    window.history.replaceState(null, "", "/agents?page=2");
    render(<DigitalWorkforceView assignments={assignments} />);

    expect(screen.getByText(assignments[5].leadName)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Search digital workforce"), { target: { value: assignments[0].leadName } });

    expect(screen.getByText(assignments[0].leadName)).toBeInTheDocument();
    expect(screen.getByText("Showing 1-1 of 1")).toBeInTheDocument();
    expect(window.location.search).toBe("");

    fireEvent.change(screen.getByLabelText("Search digital workforce"), { target: { value: "does not exist" } });

    expect(screen.getByText("No leads match this search.")).toBeInTheDocument();
    expect(screen.queryByText(/Showing/)).not.toBeInTheDocument();
  });

  it("renders lead information on the left and worker activity on the right", () => {
    render(<DigitalWorkerProgressView assignment={assignments[0]} worker={digitalWorkerProfile} />);

    expect(screen.getByRole("heading", { name: "SDR Digital Worker" })).toBeInTheDocument();
    expect(screen.queryByText("Preview only")).not.toBeInTheDocument();
    expect(screen.queryByText(`Preview for ${assignments[0].leadName}`)).not.toBeInTheDocument();

    const detailColumns = screen.getByText("Lead Information").closest(".detail-grid");
    expect(detailColumns).toBeInTheDocument();
    const headings = within(detailColumns as HTMLElement)
      .getAllByRole("heading")
      .map((heading) => heading.textContent);
    expect(headings).toEqual(["Lead Information", "Helpful context", "Worker activity"]);

    expect(screen.getByText(assignments[0].email)).toBeInTheDocument();
    expect(screen.getByText(assignments[0].company)).toBeInTheDocument();
    expect(screen.queryByText(leads[0].draft?.subject ?? "missing draft subject")).not.toBeInTheDocument();
    expect(screen.queryByText("Ready from lead record")).not.toBeInTheDocument();
    expect(screen.queryByText("Pending contact data")).not.toBeInTheDocument();
    expect(screen.queryByText("Required before outreach")).not.toBeInTheDocument();
    expect(screen.getByText("Assignment intake")).toBeInTheDocument();
    expect(screen.getByText("Outreach plan")).toBeInTheDocument();
    expect(screen.getByText("Email draft check")).toBeInTheDocument();
    expect(screen.getByText("Text follow-up readiness")).toBeInTheDocument();
    expect(screen.getByText("SDR check-in")).toBeInTheDocument();
    expect(screen.queryByText("Check-in log")).not.toBeInTheDocument();
    expect(screen.queryByText("SDR review required")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /pause/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve review/i })).not.toBeInTheDocument();
  });
});
