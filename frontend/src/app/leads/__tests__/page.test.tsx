import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LeadsPage from "../page";

describe("LeadsPage", () => {
  it("gates draft actions by lead draft eligibility", () => {
    render(<LeadsPage />);

    expect(screen.getAllByText("Copy draft").length).toBeGreaterThan(0);
    expect(screen.getByText("Draft pending")).toBeInTheDocument();
    expect(screen.getByText("Review flags")).toBeInTheDocument();
  });
});
