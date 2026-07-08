import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";

import { InboundLeadsView } from "@/components/features/leads/InboundLeadsView";
import { leads } from "@/lib/fixtures/leads";
import type { FixtureLead, InboundLeadQueueRow } from "@/types/lead";

const push = jest.fn();
const refresh = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
  useSearchParams: () => new URLSearchParams(window.location.search)
}));

describe("InboundLeadsView", () => {
  beforeEach(() => {
    push.mockClear();
    refresh.mockClear();
    window.history.replaceState(null, "", "/leads");
    jest.useRealTimers();
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined)
      }
    });
  });

  it("filters the queue by search text", () => {
    render(<InboundLeadsView leads={readyRows(leads)} />);

    fireEvent.change(screen.getByLabelText("Search inbound leads"), { target: { value: "Priya" } });

    expect(screen.getByText("Priya Nair")).toBeInTheDocument();
    expect(screen.queryByText("Sarah Chen")).not.toBeInTheDocument();
  });

  it("paginates the queue and updates the page query parameter", () => {
    render(<InboundLeadsView leads={readyRows(leads)} />);

    expect(screen.getByText("Showing 1-5 of 8")).toBeInTheDocument();
    expect(screen.getByText("Sarah Chen")).toBeInTheDocument();
    expect(screen.queryByText("Lin Zhao")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Next page" }));

    expect(screen.getByText("Showing 6-8 of 8")).toBeInTheDocument();
    expect(screen.getByText("Lin Zhao")).toBeInTheDocument();
    expect(screen.queryByText("Sarah Chen")).not.toBeInTheDocument();
    expect(window.location.search).toBe("?page=2");

    fireEvent.click(screen.getByRole("button", { name: "Previous page" }));

    expect(screen.getByText("Showing 1-5 of 8")).toBeInTheDocument();
    expect(window.location.search).toBe("");
  });

  it("resets pagination when filters or search change", () => {
    window.history.replaceState(null, "", "/leads?page=2");
    render(<InboundLeadsView leads={readyRows(leads)} />);

    expect(screen.getByText("Lin Zhao")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Search inbound leads"), { target: { value: "Priya" } });

    expect(screen.getByText("Priya Nair")).toBeInTheDocument();
    expect(screen.queryByText("Lin Zhao")).not.toBeInTheDocument();
    expect(screen.getByText("Showing 1-1 of 1")).toBeInTheDocument();
    expect(window.location.search).toBe("");
  });

  it("copies a draft with visible feedback and does not expose copy for gate-failed leads", async () => {
    render(<InboundLeadsView leads={readyRows(leads)} />);

    fireEvent.click(screen.getAllByRole("button", { name: /copy draft/i })[0]);

    await waitFor(() => expect(navigator.clipboard.writeText).toHaveBeenCalled());
    await waitFor(() => expect(screen.getByText(/Draft copied for Sarah Chen/)).toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: "Next page" }));

    expect(screen.getByText("Review flags")).toBeInTheDocument();
  });

  it("renders loading lead rows without navigation affordances", () => {
    render(<InboundLeadsView leads={[loadingRow()]} />);

    expect(screen.getByText("Sample Contact")).toBeInTheDocument();
    expect(screen.getByText("VP Leasing")).toBeInTheDocument();
    expect(screen.getByText("Multifamily Operator")).toBeInTheDocument();
    expect(screen.getByText("Austin, TX")).toBeInTheDocument();
    expect(screen.getByText("Pending")).toBeInTheDocument();
    expect(screen.getByText("Agent analysis in progress")).toBeInTheDocument();
    expect(screen.getByLabelText("Agent Running")).toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();

    const row = screen.getByText("Sample Contact").closest(".table-row");
    expect(row).not.toBeNull();
    fireEvent.click(row as Element);
    fireEvent.keyDown(row as Element, { key: "Enter" });

    expect(push).not.toHaveBeenCalled();
  });

  it("refreshes the route only while loading rows exist", () => {
    jest.useFakeTimers();
    const { rerender } = render(<InboundLeadsView leads={[loadingRow()]} />);

    act(() => {
      jest.advanceTimersByTime(3000);
    });
    expect(refresh).toHaveBeenCalledTimes(1);

    rerender(<InboundLeadsView leads={readyRows([leads[0]])} />);
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    expect(refresh).toHaveBeenCalledTimes(1);
  });
});

function readyRows(source: FixtureLead[]): InboundLeadQueueRow[] {
  return source.map((lead) => ({
    state: "ready",
    key: lead.runId ?? lead.id,
    id: lead.id,
    runId: lead.runId,
    input: {
      contact_name: lead.name,
      email: lead.email,
      company: lead.company,
      role: lead.role,
      property_address: "",
      city: lead.market.split(",")[0]?.trim() || lead.market,
      state: lead.market.split(",")[1]?.trim() || "",
      country: "US"
    },
    lead,
    run: null
  }));
}

function loadingRow(): InboundLeadQueueRow {
  return {
    state: "loading",
    key: "21111111-aaaa-4aaa-8aaa-111111111111",
    id: "11111111-aaaa-4aaa-8aaa-111111111111",
    runId: "21111111-aaaa-4aaa-8aaa-111111111111",
    input: {
      contact_name: "Sample Contact",
      email: "contact@operator.example",
      company: "Multifamily Operator",
      role: "VP Leasing",
      property_address: "100 Main St",
      city: "Austin",
      state: "TX",
      country: "US"
    },
    run: {
      run_id: "21111111-aaaa-4aaa-8aaa-111111111111",
      lead_id: "11111111-aaaa-4aaa-8aaa-111111111111",
      status: "running",
      trigger: "api_insert",
      current_stage: "agent_execution",
      steps: [],
      activity_log: []
    }
  };
}
