import { ChevronLeft, Copy, Pause, Pencil } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { PageHeader } from "@/components/ui/PageHeader";
import { PipelineStepper } from "@/components/ui/PipelineStepper";
import { getAgentRun, getLead } from "@/lib/fixtures/leads";

interface Props {
  params: Promise<{ runId: string }>;
}

export default async function AgentRunPage({ params }: Props) {
  const { runId } = await params;
  const run = getAgentRun(runId);
  if (!run) {
    notFound();
  }
  const lead = run.leadId ? getLead(run.leadId) : undefined;
  const exported = run.steps.some((step) => step.name === "Export" && step.status === "done");
  const completedWithoutDraft = Boolean(lead && !lead.draft && run.status === "completed");
  const awaitingReview = Boolean(lead?.draft && run.status === "awaiting_review");
  const outputResolved = Boolean(lead && (awaitingReview || exported || completedWithoutDraft));
  const scoreLabel = outputResolved && lead ? `${lead.score.total} · ${lead.score.tier}` : "Pending";

  const stepDetails = run.steps.map((step, index) => ({
    ...step,
    duration: step.duration ?? ["3.1s", "6.4s", "0.8s", "now", "pending"][index],
    chips:
      step.chips ??
      (index === 0 && step.status === "done"
        ? ["Address check", "Census", "Market data", "News", "MX/DNS"]
        : undefined)
  }));

  return (
    <>
      <PageHeader
        title={run.agent}
        subtitle={`${run.runId} · Working ${run.lead}`}
        actions={
          <div className="flex flex-wrap gap-2">
            <Link className="button secondary" href="/agents">
              <ChevronLeft size={16} /> Back
            </Link>
            <span className={`status-pill ${awaitingReview ? "warning" : "muted"}`}>
              {awaitingReview ? "Awaiting your review" : run.statusLabel ?? run.status}
            </span>
            {run.status === "running" && (
              <button className="button secondary" type="button">
                <Pause size={15} /> Pause
              </button>
            )}
            {awaitingReview && (
              <button className="button primary" type="button">
                <Pencil size={15} /> Review draft
              </button>
            )}
          </div>
        }
      />
      <main className="content stack-lg">
        <section className="grid gap-3 md:grid-cols-4">
          {[
            ["Trigger", "API insert"],
            ["Started", run.started],
            ["Runtime", "10.3s"],
            ["APIs called", "6 / 6"]
          ].map(([label, value]) => (
            <div key={label} className="metric-card">
              <span className="eyebrow block">{label}</span>
              <strong className="mono mt-1 block text-sm">{value}</strong>
            </div>
          ))}
        </section>
        <section className="detail-grid">
          <div className="surface-card p-5">
            <h2 className="section-title">Pipeline</h2>
            <div className="mt-5">
              <PipelineStepper steps={stepDetails} />
            </div>
          </div>
          <div className="stack">
            <div className="surface-card p-5">
              <h2 className="section-title">Activity log</h2>
              <pre className="activity-log mono">
                {run.activityLog.join("\n")}
              </pre>
            </div>
            <div className="surface-card purple-panel p-5">
              <div className="flex items-center justify-between gap-3">
                <h2 className="section-title text-deep">
                  {awaitingReview
                    ? "Output ready for review"
                    : exported
                      ? "Draft exported"
                      : completedWithoutDraft
                        ? "No draft generated"
                        : "Output in progress"}
                </h2>
                <span className="mono text-xs font-semibold text-deep">{scoreLabel}</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-muted">
                {awaitingReview
                  ? "Score, why-line, talking points, related context, and draft are ready for SDR review."
                  : exported
                    ? "The reviewed draft has been exported for use in existing sales tools."
                    : completedWithoutDraft
                      ? "This run completed without a draft because draft eligibility was not met."
                      : "Signal is still building the score, related context, and draft eligibility decision."}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {awaitingReview && (
                  <>
                    <button className="button primary" type="button">
                      <Copy size={14} /> Copy reviewed draft
                    </button>
                    <button className="button purple" type="button">
                      <Pencil size={14} /> Edit draft
                    </button>
                  </>
                )}
                {lead && (
                  <Link className="button purple" href={`/leads/${lead.id}`}>
                    View lead
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
