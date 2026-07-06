import { render, screen } from "@testing-library/react";
import { usePathname } from "next/navigation";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppShell } from "@/components/layout/AppShell";
import { routes } from "@/lib/constants/routes";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn()
}));

const mockedUsePathname = vi.mocked(usePathname);

describe("AppShell", () => {
  beforeEach(() => {
    mockedUsePathname.mockReturnValue(routes.dashboard);
  });

  it("renders stable navigation labels and workspace content", () => {
    render(<AppShell>Queue content</AppShell>);

    expect(screen.getByRole("navigation", { name: /primary navigation/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /dashboard/i })).toHaveAttribute("href", routes.dashboard);
    expect(screen.getByRole("link", { name: /inbound leads/i })).toHaveAttribute("href", routes.leads);
    expect(screen.getByRole("link", { name: /agent runs/i })).toHaveAttribute("href", routes.agents);
    expect(screen.getByText("Queue content")).toBeInTheDocument();
  });

  it("keeps the leads item active on lead detail routes", () => {
    mockedUsePathname.mockReturnValue(routes.leadDetail("lead-demo"));

    render(<AppShell>Lead detail</AppShell>);

    expect(screen.getByRole("link", { name: /inbound leads/i })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: /dashboard/i })).not.toHaveAttribute("aria-current");
  });

  it("keeps the agent item active on agent run routes", () => {
    mockedUsePathname.mockReturnValue(routes.agentRun("run-demo"));

    render(<AppShell>Agent run</AppShell>);

    expect(screen.getByRole("link", { name: /agent runs/i })).toHaveAttribute("aria-current", "page");
  });
});
