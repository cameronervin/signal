import { ChevronLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { PageHeader } from "@/components/ui/PageHeader";
import { getAgentRun } from "@/lib/fixtures/leads";

interface Props {
  params: Promise<{ runId: string }>;
}

export default async function AgentRunPage({ params }: Props) {
  const { runId } = await params;
  const run = getAgentRun(runId);
  if (!run) {
    notFound();
  }

  return (
    <>
      <PageHeader
        title={run.agent}
        subtitle={`${run.runId} · Working ${run.lead}`}
        actions={
          <div className="flex gap-2">
            <Link className="button secondary" href="/agents"><ChevronLeft size={16} /> Back</Link>
            <button className="button secondary" type="button">Pause</button>
            <button className="button primary" type="button">Approve and send</button>
          </div>
        }
      />
      <main className="content stack">
        <section className="grid gap-3 md:grid-cols-4">
          {[
            ["Trigger", "API insert"],
            ["Started", run.started],
            ["Runtime", "10.3s"],
            ["APIs called", "6 / 6"]
          ].map(([label, value]) => (
            <div key={label} className="surface-card p-4">
              <span className="mono block text-[10px] uppercase text-[var(--ink-400)]">{label}</span>
              <strong className="mono mt-1 block text-lg">{value}</strong>
            </div>
          ))}
        </section>
        <section className="detail-grid">
          <div className="surface-card p-5">
            <h2 className="section-title">Pipeline</h2>
            <ol className="mt-5 grid gap-4">
              {run.steps.map((step, index) => (
                <li key={step.name} className="grid grid-cols-[28px_1fr] gap-3">
                  <span className={`mt-0.5 flex h-5 w-5 items-center justify-center rounded-full text-xs font-bold ${step.status === "done" ? "bg-[var(--brand-primary)] text-white" : "border border-[var(--border)] bg-white"}`}>
                    {index + 1}
                  </span>
                  <span>
                    <strong className="block text-sm">{step.name}</strong>
                    <span className="text-sm leading-6 text-[var(--ink-600)]">{step.summary}</span>
                  </span>
                </li>
              ))}
            </ol>
          </div>
          <div className="stack">
            <div className="surface-card p-5">
              <h2 className="section-title">Activity log</h2>
              <pre className="mono mt-4 whitespace-pre-wrap rounded-lg bg-[var(--surface-2)] p-4 text-xs leading-6 text-[var(--ink-600)]">
                {run.activityLog.join("\n")}
              </pre>
            </div>
            <div className="surface-card border-[var(--border-purple)] bg-[#FAF9FE] p-5">
              <h2 className="section-title">Output ready for review</h2>
              <p className="mt-3 text-sm leading-6 text-[var(--ink-600)]">
                Score, why-line, talking points, related context, and draft are ready for SDR review.
              </p>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
