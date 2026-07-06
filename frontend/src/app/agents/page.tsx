import { BadgeCheck, ChevronRight, FileText, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { agentRuns } from "@/lib/fixtures/leads";

export default function AgentsPage() {
  return (
    <>
      <PageHeader
        title="Agent Assignment"
        subtitle={`${agentRuns.length} agents working`}
        actions={
          <div className="flex gap-2">
            <button className="button secondary" type="button">
              <SlidersHorizontal size={16} /> Filter
            </button>
            <SearchInput label="Search agent runs" placeholder="Search agents..." />
          </div>
        }
      />
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
            {agentRuns.map((run) => {
              const cells = (
                <>
                  <span>
                    <span className="flex items-center gap-3">
                      <span className={`icon-tile ${run.agent.includes("Enrichment") ? "neutral" : ""}`}>
                        {run.agent.includes("Enrichment") ? <BadgeCheck size={16} /> : <FileText size={15} />}
                      </span>
                      <span>
                        <strong className="block text-sm">{run.agent}</strong>
                        <span className="text-xs text-muted">{run.kind}</span>
                      </span>
                    </span>
                  </span>
                  <span className="text-sm font-semibold">{run.lead}</span>
                  <span className="mono text-sm">{run.started}</span>
                  <span>
                    <span className="mb-2 block text-sm font-semibold">{run.stage}</span>
                    <span className="progress-segments">
                      {Array.from({ length: 4 }).map((_, index) => (
                        <span
                          key={index}
                          className={
                            index < run.stageIndex ? "done" : index === run.stageIndex && !run.disabled ? "active" : ""
                          }
                        />
                      ))}
                    </span>
                  </span>
                  <span
                    className={`status-pill ${
                      run.status === "running" ? "warning" : run.disabled ? "muted" : ""
                    }`}
                  >
                    {run.statusLabel ?? run.status}
                  </span>
                  {!run.disabled && <ChevronRight className="chevron-soft" size={18} />}
                </>
              );

              return run.disabled ? (
                <div key={run.runId} className="table-row agent-grid dimmed">
                  {cells}
                </div>
              ) : (
                <Link key={run.runId} href={`/agents/${run.runId}`} className="table-row agent-grid">
                  {cells}
                </Link>
              );
            })}
          </div>
        </section>
      </main>
    </>
  );
}
