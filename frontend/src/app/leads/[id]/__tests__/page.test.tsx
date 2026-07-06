import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LeadDetailPage from "../page";

describe("LeadDetailPage", () => {
  it("shows copy and export controls when a draft exists", async () => {
    render(await LeadDetailPage({ params: Promise.resolve({ id: "lead-sarah-chen" }) }));

    expect(screen.getByRole("button", { name: /copy/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /export/i })).toBeInTheDocument();
  });

  it("withholds copy and export controls when a gate-passed lead has no draft", async () => {
    render(await LeadDetailPage({ params: Promise.resolve({ id: "lead-elena-ramos" }) }));

    expect(screen.getByText("Draft pending")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /copy/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /export/i })).not.toBeInTheDocument();
  });

  it("keeps gate-failed leads in a no-draft state", async () => {
    render(await LeadDetailPage({ params: Promise.resolve({ id: "lead-tom-whitaker" }) }));

    expect(screen.getByText("No draft generated")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /copy/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /export/i })).not.toBeInTheDocument();
  });
});
