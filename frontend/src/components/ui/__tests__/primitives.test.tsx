import { render, screen } from "@testing-library/react";
import { Check, Copy, Search } from "lucide-react";
import { describe, expect, it } from "vitest";

import { Button } from "@/components/ui/Button";
import { Flag } from "@/components/ui/Flag";
import { MetricCard } from "@/components/ui/MetricCard";
import { PipelineStepper } from "@/components/ui/PipelineStepper";
import { ScoreMeter } from "@/components/ui/ScoreMeter";
import { SearchInput } from "@/components/ui/SearchInput";
import { SourceChip } from "@/components/ui/SourceChip";
import { StateNotice } from "@/components/ui/StateNotice";
import { TierBadge } from "@/components/ui/TierBadge";

describe("UI primitives", () => {
  it("renders scoring, source, flag, search, metric, and pipeline primitives", () => {
    render(
      <>
        <TierBadge tier="A" />
        <ScoreMeter score={82} tier="A" size="large" />
        <SourceChip source={{ source: "Fixture", label: "Signal", value: "Resolved" }} />
        <Flag>Gate failed</Flag>
        <SearchInput label="Search queue" placeholder="Search..." />
        <MetricCard label="Ready drafts" value="12" detail="Awaiting review" tone="caution" />
        <PipelineStepper
          steps={[
            { name: "Enrichment", status: "done", summary: "Resolved public data." },
            { name: "Drafting", status: "running", summary: "Building reviewed output." }
          ]}
        />
      </>
    );

    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByLabelText("Score 82")).toBeInTheDocument();
    expect(screen.getByText(/Fixture/i)).toBeInTheDocument();
    expect(screen.getByText("Gate failed")).toBeInTheDocument();
    expect(screen.getByRole("searchbox", { name: /search queue/i })).toBeInTheDocument();
    expect(screen.getByText("Ready drafts")).toBeInTheDocument();
    expect(screen.getByText("Drafting")).toBeInTheDocument();
  });

  it("renders reusable buttons with stable accessible names", () => {
    render(
      <>
        <Button icon={Copy}>Copy draft</Button>
        <Button aria-label="Confirm review" icon={Check} size="icon" />
        <Button href="/leads" icon={Search} variant="secondary">
          Browse leads
        </Button>
      </>
    );

    expect(screen.getByRole("button", { name: /copy draft/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /confirm review/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /browse leads/i })).toHaveAttribute("href", "/leads");
  });

  it("renders gate-failed and degraded states as first-class visual primitives", () => {
    render(
      <>
        <StateNotice
          action={<Button variant="secondary">Verify manually</Button>}
          description="Draft generation is suppressed until the failed gates are resolved."
          title="No draft generated"
          tone="danger"
        />
        <StateNotice
          description="Showing cached enrichment with a warning for SDR review."
          eyebrow="Provider degraded"
          title="Using fixture fallback"
          tone="warning"
        />
      </>
    );

    expect(screen.getByRole("status", { name: /no draft generated/i })).toHaveTextContent(
      /draft generation is suppressed/i
    );
    expect(screen.getByRole("status", { name: /using fixture fallback/i })).toHaveTextContent(
      /provider degraded/i
    );
  });
});
