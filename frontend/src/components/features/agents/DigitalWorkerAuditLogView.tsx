"use client";

import { ChevronLeft, Mail } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import {
  buildActivityEvents,
  type ActivityTimelineEvent,
  type TimelineEmail
} from "@/components/features/agents/digitalWorkerActivity";
import { DigitalWorkerAutoRefresh } from "@/components/features/agents/DigitalWorkerAutoRefresh";
import { PageHeader } from "@/components/ui/PageHeader";
import { routes } from "@/lib/constants/routes";
import type { DigitalWorkerAssignmentDetail, DigitalWorkerProfile } from "@/types/digital-workforce";

interface Props {
  assignment: DigitalWorkerAssignmentDetail;
  worker: DigitalWorkerProfile;
}

export function DigitalWorkerAuditLogView({ assignment, worker }: Props) {
  const [openEmailId, setOpenEmailId] = useState<string | null>(assignment.draftEmail?.id ?? null);
  const events = buildActivityEvents(assignment);

  return (
    <>
      <DigitalWorkerAutoRefresh enabled={assignment.status === "active" || assignment.status === "paused"} />
      <PageHeader
        title="Audit Log"
        subtitle={`${worker.displayName} · ${assignment.assignmentStatus}`}
        actions={
          <Link className="button secondary" href={routes.digitalWorkerProgress(assignment.assignmentId)}>
            <ChevronLeft size={16} /> Back to worker
          </Link>
        }
      />
      <main className="content audit-log-screen">
        <section
          aria-labelledby="audit-log-title"
          className="surface-card audit-log-modal p-5"
          role="dialog"
        >
          <div className="flex min-w-0 flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 className="section-title" id="audit-log-title">
                Full activity
              </h2>
              <p className="mt-1 text-xs font-semibold text-[var(--ink-600)]">
                Sanitized worker events and linked communication previews for this assignment.
              </p>
            </div>
            <span className="filter-chip active">{assignment.status}</span>
          </div>
          <AuditTimeline events={events} openEmailId={openEmailId} onOpenEmailChange={setOpenEmailId} />
        </section>
      </main>
    </>
  );
}

function AuditTimeline({
  events,
  onOpenEmailChange,
  openEmailId
}: {
  events: ActivityTimelineEvent[];
  onOpenEmailChange: (emailId: string | null) => void;
  openEmailId: string | null;
}) {
  if (events.length === 0) {
    return <p className="mt-5 text-sm font-semibold text-[var(--ink-500)]">No worker events recorded yet.</p>;
  }

  return (
    <ol className="worker-event-timeline audit-event-timeline">
      {events.map((event) => {
        const email = event.email;
        const emailOpen = email ? openEmailId === email.id : false;

        return (
          <li key={event.id} className="worker-event">
            <span className="worker-event-rail" aria-hidden="true">
              <span className={email ? "worker-event-dot email" : "worker-event-dot"} />
            </span>
            <article className="worker-event-content">
              <div className="flex min-w-0 flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3>{event.title}</h3>
                  {event.occurredAt && <span className="mono worker-event-time">{formatDate(event.occurredAt)}</span>}
                </div>
                {email && (
                  <button
                    aria-expanded={emailOpen}
                    className="button purple small"
                    type="button"
                    onClick={() => onOpenEmailChange(emailOpen ? null : email.id)}
                  >
                    <Mail size={14} /> {emailOpen ? "Hide email" : "View email"}
                  </button>
                )}
              </div>
              <p>{event.detail}</p>
              {email && emailOpen && <EmailPreview email={email} />}
            </article>
          </li>
        );
      })}
    </ol>
  );
}

function EmailPreview({ email }: { email: TimelineEmail }) {
  return (
    <article className="timeline-email-preview">
      <span className="mono text-[10px] font-bold uppercase text-[var(--ink-400)]">{email.label}</span>
      <strong>{email.subject}</strong>
      <p>{email.body}</p>
      {email.sources.length > 0 && (
        <div className="timeline-email-sources">
          {email.sources.map((source) => (
            <span key={`${source.source}-${source.label}-${source.value}`} className="source-chip">
              {source.source} · {source.label}
            </span>
          ))}
        </div>
      )}
    </article>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
