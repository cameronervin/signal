"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { PageHeader } from "@/components/ui/PageHeader";
import { ScoreMeter } from "@/components/ui/ScoreMeter";
import { SearchInput } from "@/components/ui/SearchInput";
import { TablePagination } from "@/components/ui/TablePagination";
import { TierBadge } from "@/components/ui/TierBadge";
import { routes } from "@/lib/constants/routes";
import { useTablePagination } from "@/lib/hooks/useTablePagination";
import { cn } from "@/lib/utils/cn";
import type { DigitalWorkerAssignmentPreview } from "@/types/digital-workforce";

interface Props {
  assignments: DigitalWorkerAssignmentPreview[];
  leadsUnavailable?: boolean;
}

interface AssignmentRowProps {
  assignment: DigitalWorkerAssignmentPreview;
}

export function DigitalWorkforceView({ assignments, leadsUnavailable = false }: Props) {
  const [search, setSearch] = useState("");
  const filteredAssignments = useMemo(() => {
    const query = search.trim().toLowerCase();
    return assignments.filter((assignment) => {
      if (!query) {
        return true;
      }

      return [assignment.leadName, assignment.leadRole, assignment.company, assignment.market, assignment.assignmentStatus]
        .join(" ")
        .toLowerCase()
        .includes(query);
    });
  }, [assignments, search]);
  const { currentPage, endIndex, pageCount, pageItems, setPage, startIndex, totalItems } = useTablePagination({
    items: filteredAssignments
  });

  function updateSearch(value: string) {
    setSearch(value);
    setPage(1);
  }

  return (
    <>
      <PageHeader
        title="Digital Workforce"
        subtitle={`${assignments.length} eligible inbound leads`}
        actions={
          <div className="toolbar-row">
            <SearchInput label="Search digital workforce" placeholder="Search leads..." value={search} onChange={updateSearch} />
          </div>
        }
      />
      <main className="content stack-lg screen-fit digital-workforce-screen">
        {leadsUnavailable && (
          <section className="surface-card p-4 text-sm font-semibold text-[var(--amber-text)]">
            Signal could not load live leads, so Digital Workforce is showing an empty preview.
          </section>
        )}
        <section className="surface-card data-table">
          <div className="table-row table-head digital-workforce-grid mono">
            <span>Tier</span>
            <span>Lead</span>
            <span>Score</span>
            <span>Channels</span>
            <span>Assignment preview</span>
            <span />
          </div>
          <div className="table-body">
            {pageItems.map((assignment) => (
              <AssignmentRow key={assignment.previewId} assignment={assignment} />
            ))}
            {filteredAssignments.length === 0 && (
              <div className="empty-table-row">
                {assignments.length === 0 ? "No eligible draft-ready leads are available." : "No leads match this search."}
              </div>
            )}
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

function AssignmentRow({ assignment }: AssignmentRowProps) {
  return (
    <Link
      className={cn("table-row digital-workforce-grid")}
      href={routes.digitalWorkerProgress(assignment.previewId)}
    >
      <TierBadge tier={assignment.tier} />
      <span className="table-cell cell-stack" data-label="Lead">
        <strong>{assignment.leadName}</strong>
        <span>
          {assignment.leadRole} · {assignment.company} · {assignment.market}
        </span>
      </span>
      <span className="table-cell score-cell" data-label="Score">
        <ScoreMeter score={assignment.score} tier={assignment.tier} />
      </span>
      <span className="table-cell channel-readiness" data-label="Channels">
        <span>Email: {assignment.channelReadiness.email}</span>
        <span>Text: {assignment.channelReadiness.text}</span>
        <span>Review: {assignment.channelReadiness.humanReview}</span>
      </span>
      <span className="table-cell assignment-preview-cell" data-label="Assignment preview">
        <span className="mb-2 block text-sm font-semibold">{assignment.assignmentStatus}</span>
        <span className="text-xs leading-5 text-[var(--ink-600)]">{assignment.summary}</span>
      </span>
      <ChevronRight size={18} color="var(--ink-400)" />
    </Link>
  );
}
