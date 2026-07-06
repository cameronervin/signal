import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import AgentRunPage from "../page";

describe("AgentRunPage", () => {
  it("shows review actions only for runs awaiting human review", async () => {
    render(await AgentRunPage({ params: Promise.resolve({ runId: "run-8842" }) }));

    expect(screen.getByText("Output ready for review")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /copy reviewed draft/i })).toBeInTheDocument();
  });

  it("withholds review actions while scoring is in progress", async () => {
    render(await AgentRunPage({ params: Promise.resolve({ runId: "run-9011" }) }));

    expect(screen.getByText("Output in progress")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /review draft/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /copy reviewed draft/i })).not.toBeInTheDocument();
  });

  it("preserves exported runs as terminal states", async () => {
    render(await AgentRunPage({ params: Promise.resolve({ runId: "run-7750" }) }));

    expect(screen.getByText("Exported")).toBeInTheDocument();
    expect(screen.getByText("Draft exported")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /pause/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /review draft/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /copy reviewed draft/i })).not.toBeInTheDocument();
  });

  it("preserves copied runs as terminal states", async () => {
    render(await AgentRunPage({ params: Promise.resolve({ runId: "run-5510" }) }));

    expect(screen.getByText("Copied")).toBeInTheDocument();
    expect(screen.getByText("Draft copied")).toBeInTheDocument();
    expect(screen.queryByText("Output in progress")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /copy reviewed draft/i })).not.toBeInTheDocument();
  });

  it("shows completed no-draft runs instead of progress or review actions", async () => {
    render(await AgentRunPage({ params: Promise.resolve({ runId: "run-6600" }) }));

    expect(screen.getByText("Gate failed")).toBeInTheDocument();
    expect(screen.getByText("No draft generated")).toBeInTheDocument();
    expect(screen.getAllByText(/skipped/i).length).toBeGreaterThan(0);
    expect(screen.queryByText("Output in progress")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /pause/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /review draft/i })).not.toBeInTheDocument();
  });
});
