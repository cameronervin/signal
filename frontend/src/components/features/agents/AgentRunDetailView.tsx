"use client";

import { ChevronLeft, Edit3, ExternalLink, Pause, SendHorizontal } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { approveAgentRun, pauseAgentRun } from "@/lib/api/endpoints/agent-runs";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { PipelineStepper } from "@/components/ui/PipelineStepper";
import { StatusPill } from "@/components/ui/StatusPill";
import { Toast } from "@/components/ui/Toast";
import { routes } from "@/lib/constants/routes";
import type { FixtureAgentRun } from "@/types/lead";

interface Props {
  run: FixtureAgentRun;
}

interface MetadataCardProps {
  label: string;
  value: string;
}

export function AgentRunDetailView({ run }: Props) {
  const [currentRun, setCurrentRun] = useState(run);
  const [pendingAction, setPendingAction] = useState<"pause" | "approve" | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const canPause = currentRun.rawStatus === "queued" || currentRun.rawStatus === "running" || currentRun.rawStatus === "awaiting_review";
  const canApprove = currentRun.rawStatus === "awaiting_review" || currentRun.status === "Awaiting you";

  async function runAction(action: "pause" | "approve") {
    setPendingAction(action);
    try {
      const updated = action === "pause" ? await pauseAgentRun(currentRun.runId) : await approveAgentRun(currentRun.runId);
      setCurrentRun(updated);
      setToast(action === "pause" ? "Agent run paused" : "Review approved. No outreach was sent.");
      window.setTimeout(() => setToast(null), 2400);
    } catch (error) {
      setToast(error instanceof Error ? error.message : "Agent run update failed");
    } finally {
      setPendingAction(null);
    }
  }

  return (
    <>
      <PageHeader
        title={currentRun.agent}
        subtitle={`${currentRun.runId} · Working ${currentRun.lead}`}
        actions={
          <div className="toolbar-row">
            <Link className="button secondary" href={routes.agents}>
              <ChevronLeft size={16} /> Back
            </Link>
            <StatusPill tone={currentRun.status === "Paused" ? "warning" : "purple"}>{currentRun.status}</StatusPill>
            <Button disabled={!canPause || pendingAction !== null} onClick={() => void runAction("pause")}>
              <Pause size={15} /> {pendingAction === "pause" ? "Pausing" : "Pause"}
            </Button>
            <Button variant="primary" disabled={!canApprove || pendingAction !== null} onClick={() => void runAction("approve")}>
              <SendHorizontal size={15} /> {pendingAction === "approve" ? "Approving" : "Approve review"}
            </Button>
          </div>
        }
      />
      <main className="content stack screen-fit agent-progress-screen">
        <Toast message={toast} />
        <section className="grid gap-3 md:grid-cols-4">
          <MetadataCard label="Started" value={currentRun.started} />
          {[
            ["Trigger", currentRun.trigger ?? "api insert"],
            ["Runtime", currentRun.runtime ?? "n/a"],
            ["APIs called", currentRun.apisCalled ?? "n/a"]
          ].map(([label, value]) => (
            <MetadataCard key={label} label={label} value={value} />
          ))}
        </section>
        <section className="detail-grid">
          <div className="surface-card p-5">
            <h2 className="section-title">Pipeline</h2>
            <PipelineStepper steps={currentRun.steps} />
          </div>
          <div className="stack">
            <div className="surface-card p-5">
              <h2 className="section-title">Activity log</h2>
              <pre className="activity-log mono mt-4 whitespace-pre-wrap rounded-lg bg-[var(--surface-2)] p-4 text-xs leading-6 text-[var(--ink-600)]">
                {currentRun.activityLog.join("\n")}
              </pre>
            </div>
            <div className="surface-card review-panel p-5">
              <div className="review-panel-header">
                <h2 className="section-title">Output ready for review</h2>
                {currentRun.output && (
                  <span className="mono review-score">
                    {currentRun.output.score} · {currentRun.output.tier}
                  </span>
                )}
              </div>
              <p className="mt-3 text-sm leading-6 text-[var(--ink-600)]">
                {currentRun.output?.summary ??
                  "Score, why-line, sales insights, related context, and draft are ready for SDR review."}
              </p>
              <div className="review-actions">
                <Button variant="primary" disabled={!canApprove || pendingAction !== null} onClick={() => void runAction("approve")}>
                  Approve review
                </Button>
                <Button>
                  <Edit3 size={15} /> Edit draft
                </Button>
                {currentRun.output && (
                  <Link className="button purple" href={routes.leadDetail(currentRun.output.leadId)}>
                    <ExternalLink size={15} /> View lead
                  </Link>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}

function MetadataCard({ label, value }: MetadataCardProps) {
  return (
    <div className="surface-card p-4">
      <span className="mono block text-[10px] uppercase text-[var(--ink-400)]">{label}</span>
      <strong className="mono mt-1 block text-lg">{value}</strong>
    </div>
  );
}
