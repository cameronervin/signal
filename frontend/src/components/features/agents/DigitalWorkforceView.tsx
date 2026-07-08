"use client";

import { ChevronRight, Plus } from "lucide-react";
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
import type { DigitalWorkerAssignmentRow } from "@/types/digital-workforce";

type FormAction = (formData: FormData) => void | Promise<void>;

interface Props {
  assignments: DigitalWorkerAssignmentRow[];
  createAssignmentAction: FormAction;
  dataUnavailable?: boolean;
}

interface AssignmentRowProps {
  assignment: DigitalWorkerAssignmentRow;
  createAssignmentAction: FormAction;
}

export function DigitalWorkforceView({ assignments, createAssignmentAction, dataUnavailable = false }: Props) {
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
        subtitle={`${assignments.length} worker-ready leads`}
        actions={
          <div className="toolbar-row">
            <SearchInput label="Search digital workforce" placeholder="Search leads..." value={search} onChange={updateSearch} />
          </div>
        }
      />
      <main className="content stack-lg screen-fit digital-workforce-screen">
        {dataUnavailable && (
          <section className="surface-card p-4 text-sm font-semibold text-[var(--amber-text)]">
            Signal could not load Digital Worker data from the API.
          </section>
        )}
        <section className="surface-card data-table">
          <div className="table-row table-head digital-workforce-grid mono">
            <span>Tier</span>
            <span>Lead</span>
            <span>Score</span>
            <span>Channels</span>
            <span>Assignment status</span>
            <span />
          </div>
          <div className="table-body">
            {pageItems.map((assignment) => (
              <AssignmentRow
                key={assignment.rowId}
                assignment={assignment}
                createAssignmentAction={createAssignmentAction}
              />
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

function AssignmentRow({ assignment, createAssignmentAction }: AssignmentRowProps) {
  const content = (
    <>
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
      <span className="table-cell assignment-preview-cell" data-label="Assignment status">
        <span className="mb-2 block text-sm font-semibold">{assignment.assignmentStatus}</span>
        <span className="text-xs leading-5 text-[var(--ink-600)]">{assignment.summary}</span>
      </span>
    </>
  );

  if (assignment.assignmentId) {
    return (
      <Link
        className={cn("table-row digital-workforce-grid")}
        href={routes.digitalWorkerProgress(assignment.assignmentId)}
      >
        {content}
        <ChevronRight size={18} color="var(--ink-400)" />
      </Link>
    );
  }

  return (
    <div className={cn("table-row digital-workforce-grid")}>
      {content}
      <form action={createAssignmentAction} className="assignment-action-cell">
        <input name="leadId" type="hidden" value={assignment.leadId} />
        <button className="button primary small" type="submit">
          <Plus size={14} /> Assign
        </button>
      </form>
    </div>
  );
}
