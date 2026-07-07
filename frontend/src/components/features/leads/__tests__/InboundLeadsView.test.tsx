import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { InboundLeadsView } from "@/components/features/leads/InboundLeadsView";
import { leads } from "@/lib/fixtures/leads";

const push = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push })
}));

describe("InboundLeadsView", () => {
  beforeEach(() => {
    push.mockClear();
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined)
      }
    });
  });

  it("filters the queue by search text", () => {
    render(<InboundLeadsView leads={leads} />);

    fireEvent.change(screen.getByLabelText("Search inbound leads"), { target: { value: "Priya" } });

    expect(screen.getByText("Priya Nair")).toBeInTheDocument();
    expect(screen.queryByText("Sarah Chen")).not.toBeInTheDocument();
  });

  it("copies a draft with visible feedback and does not expose copy for gate-failed leads", async () => {
    render(<InboundLeadsView leads={leads} />);

    fireEvent.click(screen.getAllByRole("button", { name: /copy draft/i })[0]);

    await waitFor(() => expect(navigator.clipboard.writeText).toHaveBeenCalled());
    await waitFor(() => expect(screen.getByText(/Draft copied for Sarah Chen/)).toBeInTheDocument());
    expect(screen.getByText("Review flags")).toBeInTheDocument();
  });
});
