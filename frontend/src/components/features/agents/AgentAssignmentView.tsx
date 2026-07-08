"use client";

import { CheckCircle, ChevronRight, Search, Send } from "lucide-react";
import { useMemo, useState } from "react";
import Link from "next/link";

import { FilterChip } from "@/components/ui/FilterChip";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { StatusPill } from "@/components/ui/StatusPill";
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
  const [search, setSearch] = useState("");
  const [awaitingOnly, setAwaitingOnly] = useState(false);
  const filteredRuns = useMemo(
    () =>
      agentRuns.filter((run) => {
        const query = search.trim().toLowerCase();
        const matchesSearch = !query || [run.agent, run.kind, run.lead, run.stage, run.status].join(" ").toLowerCase().includes(query);
        const matchesStatus = !awaitingOnly || run.status === "Awaiting you";
        return matchesSearch && matchesStatus;
      }),
    [agentRuns, awaitingOnly, search]
  );

  return (
    <>
      <PageHeader
        title="Agent Assignment"
        subtitle={`${filteredRuns.length} agents working`}
        actions={
          <div className="toolbar-row">
            <SearchInput label="Search agent runs" placeholder="Search runs..." value={search} onChange={setSearch} />
          </div>
        }
      />
      <main className="content stack-lg screen-fit agent-assignment-screen">
        <div className="flex flex-wrap gap-2">
          <FilterChip active={awaitingOnly} onClick={() => setAwaitingOnly((active) => !active)}>
            Awaiting you
          </FilterChip>
          <FilterChip active={false}>
            <Search size={13} /> Active runs
          </FilterChip>
        </div>
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
            {filteredRuns.map((run) => (
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
      <span className="table-cell agent-cell" data-label="Agent">
        <span className={cn("icon-tile", run.agent.includes("Enrichment") && "neutral")}>
          {run.agent.includes("Enrichment") ? <CheckCircle size={16} /> : <Send size={16} />}
        </span>
        <span className="agent-cell-copy">
          <strong>{run.agent}</strong>
          <span>{run.kind}</span>
        </span>
      </span>
      <span className="table-cell table-strong" data-label="Working lead">{run.lead}</span>
      <span className="table-cell mono" data-label="Started">{run.started}</span>
      <span className="table-cell" data-label="Stage">
        <span className="mb-2 block text-sm font-semibold">{run.stage}</span>
        <span className="progress-segments">
          {Array.from({ length: 4 }).map((_, index) => (
            <span
              key={index}
              className={cn(
                index < run.stageIndex && "done",
                index === run.stageIndex &&
                  !run.disabled &&
                  run.rawStatus !== "completed" &&
                  run.rawStatus !== "failed" &&
                  "active"
              )}
            />
          ))}
        </span>
      </span>
      <StatusPill tone={statusTone(run)} data-label="Status">{run.status}</StatusPill>
    </>
  );
}

function statusTone(run: FixtureAgentRun) {
  if (run.disabled) {
    return "muted";
  }
  if (run.rawStatus === "paused" || run.status === "In progress") {
    return "warning";
  }
  if (run.rawStatus === "failed" || run.status === "Failed") {
    return "danger";
  }
  if (run.rawStatus === "completed" || run.status === "Completed") {
    return "muted";
  }
  return "purple";
}
