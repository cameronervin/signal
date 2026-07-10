"use client";

import { ChevronRight, Copy, Loader2, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { FilterChip } from "@/components/ui/FilterChip";
import { Flag } from "@/components/ui/Flag";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { ScoreMeter } from "@/components/ui/ScoreMeter";
import { TablePagination } from "@/components/ui/TablePagination";
import { TierBadge } from "@/components/ui/TierBadge";
import { Toast } from "@/components/ui/Toast";
import { routes } from "@/lib/constants/routes";
import { useTablePagination } from "@/lib/hooks/useTablePagination";
import { cn } from "@/lib/utils/cn";
import type { FixtureLead, InboundLeadQueueRow, RunStatus } from "@/types/lead";

interface Props {
  leads: InboundLeadQueueRow[];
}

const ACTIVE_REFRESH_MS = 3000;
const PASSIVE_REFRESH_MS = 10000;

export function InboundLeadsView({ leads }: Props) {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [tierAOnly, setTierAOnly] = useState(false);
  const [corporateOnly, setCorporateOnly] = useState(false);
  const [unassignedOnly, setUnassignedOnly] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const hasLoadingRows = leads.some((row) => row.state === "loading");
  const tierACount = leads.filter((row) => row.state === "ready" && row.lead.score.tier === "A").length;
  const filteredLeads = useMemo(
    () =>
      leads.filter((row) => {
        const query = search.trim().toLowerCase();
        const matchesSearch = !query || searchableRowText(row).includes(query);
        const matchesTier = !tierAOnly || (row.state === "ready" && row.lead.score.tier === "A");
        const matchesCorporate = !corporateOnly || (row.state === "ready" && row.lead.gates.status === "passed");
        const matchesAssignment = !unassignedOnly || (row.state === "ready" && !row.lead.runId);

        return matchesSearch && matchesTier && matchesCorporate && matchesAssignment;
      }),
    [corporateOnly, leads, search, tierAOnly, unassignedOnly]
  );
  const { currentPage, endIndex, pageCount, pageItems, setPage, startIndex, totalItems } = useTablePagination({
    items: filteredLeads
  });

  useEffect(() => {
    const refreshWhenVisible = () => {
      if (document.visibilityState === "visible") {
        router.refresh();
      }
    };

    const refreshId = window.setInterval(
      refreshWhenVisible,
      hasLoadingRows ? ACTIVE_REFRESH_MS : PASSIVE_REFRESH_MS
    );
    window.addEventListener("focus", refreshWhenVisible);
    document.addEventListener("visibilitychange", refreshWhenVisible);

    return () => {
      window.clearInterval(refreshId);
      window.removeEventListener("focus", refreshWhenVisible);
      document.removeEventListener("visibilitychange", refreshWhenVisible);
    };
  }, [hasLoadingRows, router]);

  async function copyDraft(lead: FixtureLead) {
    if (!lead.draft) {
      return;
    }

    await navigator.clipboard.writeText(`${lead.draft.subject}\n\n${lead.draft.body}`);
    setToast(`Draft copied for ${lead.name}`);
    window.setTimeout(() => setToast(null), 2200);
  }

  function openLead(leadId: string) {
    router.push(routes.leadDetail(leadId));
  }

  function updateSearch(value: string) {
    setSearch(value);
    setPage(1);
  }

  return (
    <>
      <PageHeader
        title="Inbound Leads"
        subtitle={`${filteredLeads.length} open · active first`}
        actions={
          <div className="toolbar-row">
            <Button>
              <SlidersHorizontal size={16} /> Filter
            </Button>
            <SearchInput label="Search inbound leads" placeholder="Search leads..." value={search} onChange={updateSearch} />
          </div>
        }
      />
      <main className="content stack-lg screen-fit leads-screen">
        <Toast message={toast} />
        <div className="flex flex-wrap gap-2">
          <FilterChip
            active={tierAOnly}
            onClick={() => {
              setTierAOnly((active) => !active);
              setPage(1);
            }}
          >
            Tier A · {tierACount}
          </FilterChip>
          <FilterChip
            active={corporateOnly}
            onClick={() => {
              setCorporateOnly((active) => !active);
              setPage(1);
            }}
          >
            Corporate email
          </FilterChip>
          <FilterChip
            active={unassignedOnly}
            onClick={() => {
              setUnassignedOnly((active) => !active);
              setPage(1);
            }}
          >
            Unassigned
          </FilterChip>
        </div>
        <section className="surface-card data-table">
          <div className="table-row table-head lead-grid mono">
            <span>Tier</span>
            <span>Lead</span>
            <span>Company</span>
            <span>Market</span>
            <span>Units</span>
            <span>Score</span>
            <span>Why this lead</span>
            <span>Status</span>
            <span />
          </div>
          <div className="table-body">
            {pageItems.map((row) =>
              row.state === "ready" ? (
                <ReadyLeadRow key={row.key} lead={row.lead} onCopyDraft={copyDraft} onOpenLead={openLead} />
              ) : (
                <LoadingLeadRow key={row.key} row={row} />
              )
            )}
            {filteredLeads.length === 0 && <div className="empty-table-row">No leads match this search.</div>}
          </div>
          <TablePagination
            currentPage={currentPage}
            endIndex={endIndex}
            onPageChange={setPage}
            pageCount={pageCount}
            startIndex={startIndex}
            totalItems={totalItems}
          />
        </section>
      </main>
    </>
  );
}

function ReadyLeadRow({
  lead,
  onCopyDraft,
  onOpenLead
}: {
  lead: FixtureLead;
  onCopyDraft: (lead: FixtureLead) => Promise<void>;
  onOpenLead: (leadId: string) => void;
}) {
  return (
    <div
      role="link"
      tabIndex={0}
      className={cn(
        "table-row lead-grid",
        lead.score.tier === "A" && "tier-a-row",
        lead.gates.status === "failed" && "dimmed"
      )}
      onClick={() => onOpenLead(lead.id)}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          onOpenLead(lead.id);
        }
      }}
    >
      <TierBadge tier={lead.score.tier} />
      <span className="table-cell cell-stack" data-label="Lead">
        <strong>{lead.name}</strong>
        <span>{lead.role}</span>
      </span>
      <span className="table-cell table-strong" data-label="Company">
        {lead.company}
      </span>
      <span className="table-cell" data-label="Market">
        {lead.market}
      </span>
      <span className="table-cell mono" data-label="Units">
        {lead.units ? `${Math.round(lead.units / 1000)}k` : "-"}
      </span>
      <span className="table-cell" data-label="Score">
        <ScoreMeter score={lead.score.total} tier={lead.score.tier} />
      </span>
      <span className="table-cell why-cell" data-label="Why this lead">
        {lead.score.whyLine}
      </span>
      <span className="table-cell action-cell" data-label="Status">
        {lead.gates.status === "failed" ? (
          <Flag>Review flags</Flag>
        ) : (
          <Button
            size="small"
            onClick={(event) => {
              event.stopPropagation();
              void onCopyDraft(lead);
            }}
          >
            <Copy aria-hidden="true" size={14} /> Copy draft
          </Button>
        )}
      </span>
      <ChevronRight
        className="row-icon-action"
        size={18}
        color={lead.gates.status === "failed" ? "var(--muted-chev)" : "var(--ink-400)"}
      />
    </div>
  );
}

function LoadingLeadRow({ row }: { row: Extract<InboundLeadQueueRow, { state: "loading" }> }) {
  return (
    <div className="table-row lead-grid lead-loading-row" aria-disabled="true">
      <span className="table-cell queue-placeholder mono" data-label="Tier">
        -
      </span>
      <span className="table-cell cell-stack" data-label="Lead">
        <strong>{row.input.contact_name}</strong>
        <span>{row.input.role || "Role pending"}</span>
      </span>
      <span className="table-cell table-strong" data-label="Company">
        {row.input.company}
      </span>
      <span className="table-cell" data-label="Market">
        {formatSubmittedMarket(row.input.city, row.input.state)}
      </span>
      <span className="table-cell mono queue-placeholder" data-label="Units">
        -
      </span>
      <span className="table-cell queue-placeholder" data-label="Score">
        Pending
      </span>
      <span className="table-cell why-cell queue-placeholder" data-label="Why this lead">
        Agent analysis in progress
      </span>
      <span className="table-cell action-cell" data-label="Status">
        <span className="status-pill muted queue-loading-pill" aria-label={`Agent ${runStatusLabel(row.run.status)}`}>
          <Loader2 className="queue-status-spin" aria-hidden="true" size={14} />
          {runStatusLabel(row.run.status)}
        </span>
      </span>
      <span aria-hidden="true" />
    </div>
  );
}

function searchableRowText(row: InboundLeadQueueRow) {
  if (row.state === "ready") {
    const lead = row.lead;
    return [lead.name, lead.role, lead.company, lead.market, lead.score.whyLine].join(" ").toLowerCase();
  }

  return [
    row.input.contact_name,
    row.input.role,
    row.input.company,
    formatSubmittedMarket(row.input.city, row.input.state),
    row.run.current_stage,
    row.run.status
  ]
    .join(" ")
    .toLowerCase();
}

function formatSubmittedMarket(city: string, state: string) {
  return [city, state].filter(Boolean).join(", ") || "-";
}

function runStatusLabel(status: RunStatus) {
  const labels: Record<RunStatus, string> = {
    queued: "Queued",
    running: "Running",
    awaiting_review: "Ready",
    paused: "Paused",
    completed: "Completed",
    failed: "Failed"
  };

  return labels[status];
}
