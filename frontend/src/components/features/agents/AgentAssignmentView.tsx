import { ChevronRight } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/ui/PageHeader";
import { routes } from "@/lib/constants/routes";
import { cn } from "@/lib/utils/cn";
import type { FixtureAgentRun } from "@/types/lead";

interface Props {
  agentRuns: FixtureAgentRun[];
}

interface AgentRunRowProps {
  run: FixtureAgentRun;
}

export function AgentAssignmentView({ agentRuns }: Props) {
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
              <AgentRunRow key={run.runId} run={run} />
            ))}
          </div>
        </section>
      </main>
    </>
  );
}

function AgentRunRow({ run }: AgentRunRowProps) {
  const className = cn("table-row agent-grid", run.disabled && "dimmed");

  if (run.disabled) {
    return (
      <div className={className} aria-disabled="true">
        <AgentRunRowContent run={run} />
      </div>
    );
  }

  return (
    <Link href={routes.agentRunDetail(run.runId)} className={className}>
      <AgentRunRowContent run={run} />
      <ChevronRight size={18} color="var(--ink-400)" />
    </Link>
  );
}

function AgentRunRowContent({ run }: AgentRunRowProps) {
  return (
    <>
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
              className={cn(
                "h-1.5 rounded-full",
                index < run.stageIndex ? "bg-[var(--brand-primary)]" : "bg-[#EEF1F0]"
              )}
            />
          ))}
        </span>
      </span>
      <span className="rounded-md bg-[var(--brand-tint)] px-3 py-1.5 text-xs font-bold text-[var(--brand-deep)]">
        {run.status}
      </span>
    </>
  );
}
