import { ChevronLeft } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/ui/PageHeader";
import { PipelineStepper } from "@/components/ui/PipelineStepper";
import { routes } from "@/lib/constants/routes";
import type { FixtureAgentRun } from "@/types/lead";

interface Props {
  run: FixtureAgentRun;
}

interface MetadataCardProps {
  label: string;
  value: string;
}

const metadata = [
  ["Trigger", "API insert"],
  ["Runtime", "10.3s"],
  ["APIs called", "6 / 6"]
] as const;

export function AgentRunDetailView({ run }: Props) {
  return (
    <>
      <PageHeader
        title={run.agent}
        subtitle={`${run.runId} · Working ${run.lead}`}
        actions={
          <div className="flex gap-2">
            <Link className="button secondary" href={routes.agents}>
              <ChevronLeft size={16} /> Back
            </Link>
            <button className="button secondary" type="button">
              Pause
            </button>
            <button className="button primary" type="button">
              Approve and send
            </button>
          </div>
        }
      />
      <main className="content stack">
        <section className="grid gap-3 md:grid-cols-4">
          <MetadataCard label="Started" value={run.started} />
          {metadata.map(([label, value]) => (
            <MetadataCard key={label} label={label} value={value} />
          ))}
        </section>
        <section className="detail-grid">
          <div className="surface-card p-5">
            <h2 className="section-title">Pipeline</h2>
            <PipelineStepper steps={run.steps} />
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

function MetadataCard({ label, value }: MetadataCardProps) {
  return (
    <div className="surface-card p-4">
      <span className="mono block text-[10px] uppercase text-[var(--ink-400)]">{label}</span>
      <strong className="mono mt-1 block text-lg">{value}</strong>
    </div>
  );
}
