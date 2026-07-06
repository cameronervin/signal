import { ChevronRight } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/ui/PageHeader";
import { agentRuns } from "@/lib/fixtures/leads";

export default function AgentsPage() {
  return (
    <>
      <PageHeader title="Agent Assignment" subtitle={`${agentRuns.length} agents working`} />
      <main className="content">
        <section className="surface-card data-table">
          <div className="table-row table-head agent-grid mono">
            <span>Agent</span>
            <span>Working lead</span>
            <span>Started</span>
            <span>Stage</span>
            <span>Status</span>
            <span />
          </div>
          <div className="table-body">
            {agentRuns.map((run) => (
              <Link key={run.runId} href={`/agents/${run.runId}`} className={`table-row agent-grid ${run.disabled ? "dimmed" : ""}`}>
                <span>
                  <strong className="block text-sm">{run.agent}</strong>
                  <span className="text-xs text-[var(--ink-600)]">{run.kind}</span>
                </span>
                <span className="text-sm font-semibold">{run.lead}</span>
                <span className="mono text-sm">{run.started}</span>
                <span>
                  <span className="mb-2 block text-sm font-semibold">{run.stage}</span>
                  <span className="grid grid-cols-4 gap-1">
                    {Array.from({ length: 4 }).map((_, index) => (
                      <span
                        key={index}
                        className={`h-1.5 rounded-full ${index < run.stageIndex ? "bg-[var(--brand-primary)]" : "bg-[#EEF1F0]"}`}
                      />
                    ))}
                  </span>
                </span>
                <span className="rounded-md bg-[var(--brand-tint)] px-3 py-1.5 text-xs font-bold text-[var(--brand-deep)]">
                  {run.status}
                </span>
                {!run.disabled && <ChevronRight size={18} color="var(--ink-400)" />}
              </Link>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
