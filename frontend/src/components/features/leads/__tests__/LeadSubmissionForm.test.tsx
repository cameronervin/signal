import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { LeadSubmissionForm } from "@/components/features/leads/LeadSubmissionForm";
import { createLead } from "@/lib/api/endpoints/leads";
import type { AgentRunResponseDto } from "@/types/lead";

jest.mock("@/lib/api/endpoints/leads", () => ({
  createLead: jest.fn()
}));

const createLeadMock = jest.mocked(createLead);

describe("LeadSubmissionForm", () => {
  beforeEach(() => {
    createLeadMock.mockReset();
  });

  it("renders every requested field", () => {
    render(<LeadSubmissionForm />);

    expect(screen.getByLabelText("Name")).toBeInTheDocument();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByLabelText("Company")).toBeInTheDocument();
    expect(screen.getByLabelText("Role")).toBeInTheDocument();
    expect(screen.getByLabelText("Property address")).toBeInTheDocument();
    expect(screen.getByLabelText("City")).toBeInTheDocument();
    expect(screen.getByLabelText("State")).toBeInTheDocument();
    expect(screen.getByLabelText("Country")).toBeInTheDocument();
  });

  it("blocks empty submissions with inline field errors", async () => {
    render(<LeadSubmissionForm />);

    fireEvent.click(screen.getByRole("button", { name: /^submit$/i }));

    expect(await screen.findByText("Name is required.")).toBeInTheDocument();
    expect(screen.getByText("Email address is required.")).toBeInTheDocument();
    expect(screen.getByText("Company is required.")).toBeInTheDocument();
    expect(screen.getByText("Role is required.")).toBeInTheDocument();
    expect(screen.getByText("Property address is required.")).toBeInTheDocument();
    expect(screen.getByText("City is required.")).toBeInTheDocument();
    expect(screen.getByText("State is required.")).toBeInTheDocument();
    expect(createLeadMock).not.toHaveBeenCalled();
  });

  it("submits trimmed values with backend field names", async () => {
    createLeadMock.mockResolvedValueOnce(queuedRunResponse());
    render(<LeadSubmissionForm />);

    fillValidForm();
    fireEvent.click(screen.getByRole("button", { name: /^submit$/i }));

    await waitFor(() =>
      expect(createLeadMock).toHaveBeenCalledWith({
        contact_name: "Sample Contact",
        email: "contact@operator.example",
        company: "Multifamily Operator",
        role: "VP Leasing",
        property_address: "100 Main St",
        city: "Austin",
        state: "TX",
        country: "US"
      })
    );
  });

  it("shows a simple submission received message", async () => {
    createLeadMock.mockResolvedValueOnce(queuedRunResponse());
    render(<LeadSubmissionForm />);

    fillValidForm();
    fireEvent.click(screen.getByRole("button", { name: /^submit$/i }));

    expect(await screen.findByText("Submission Recieved")).toBeInTheDocument();
    expect(
      screen.getByText("Thank you for your taking the time to fill out our contact form. We look forward to working with you!")
    ).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /view run/i })).not.toBeInTheDocument();
  });

  it("shows API failure feedback without clearing entered values", async () => {
    createLeadMock.mockRejectedValueOnce(new Error("API unavailable"));
    render(<LeadSubmissionForm />);

    fillValidForm();
    fireEvent.click(screen.getByRole("button", { name: /^submit$/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Signal could not submit this lead");
    expect(screen.getByLabelText("Company")).toHaveValue(" Multifamily Operator ");
  });
});

function fillValidForm() {
  fireEvent.change(screen.getByLabelText("Name"), { target: { value: " Sample Contact " } });
  fireEvent.change(screen.getByLabelText("Email address"), { target: { value: " contact@operator.example " } });
  fireEvent.change(screen.getByLabelText("Company"), { target: { value: " Multifamily Operator " } });
  fireEvent.change(screen.getByLabelText("Role"), { target: { value: " VP Leasing " } });
  fireEvent.change(screen.getByLabelText("Property address"), { target: { value: " 100 Main St " } });
  fireEvent.change(screen.getByLabelText("City"), { target: { value: " Austin " } });
  fireEvent.change(screen.getByLabelText("State"), { target: { value: " TX " } });
  fireEvent.change(screen.getByLabelText("Country"), { target: { value: " US " } });
}

function queuedRunResponse(): AgentRunResponseDto {
  return {
    run_id: "21111111-1111-4111-8111-111111111111",
    lead_id: "11111111-1111-4111-8111-111111111111",
    status: "queued",
    trigger: "api_insert",
    current_stage: "queued",
    steps: [],
    activity_log: ["api_insert: lead received", "agent_run: queued"]
  };
}
