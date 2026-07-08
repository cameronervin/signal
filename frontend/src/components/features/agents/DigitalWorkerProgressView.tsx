"use client";

import { Bot, Check, ChevronLeft, ExternalLink, Pause, Play } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { DigitalWorkerAutoRefresh } from "@/components/features/agents/DigitalWorkerAutoRefresh";
import { communicationForStep, type TimelineEmail } from "@/components/features/agents/digitalWorkerActivity";
import { routes } from "@/lib/constants/routes";
import type {
  DigitalWorkerAssignmentDetail,
  DigitalWorkerAssignmentRow,
  DigitalWorkerProfile,
  DigitalWorkerStepStatus
} from "@/types/digital-workforce";

type FormAction = (formData: FormData) => void | Promise<void>;

interface Props {
  assignment: DigitalWorkerAssignmentDetail;
  pauseAssignmentAction: FormAction;
  resumeAssignmentAction: FormAction;
  worker: DigitalWorkerProfile;
}

interface MetadataCardProps {
  label: string;
  value: string;
}

export function DigitalWorkerProgressView({
  assignment,
  pauseAssignmentAction,
  resumeAssignmentAction,
  worker
}: Props) {
  return (
    <>
      <DigitalWorkerAutoRefresh enabled={assignment.status === "active" || assignment.status === "paused"} />
      <PageHeader
        title="SDR Digital Worker"
        subtitle={`${worker.displayName} · ${assignment.assignmentStatus}`}
        actions={
          <div className="toolbar-row">
            <Link className="button secondary" href={routes.digitalWorkforce}>
              <ChevronLeft size={16} /> Back
            </Link>
            <AssignmentStatusAction
              assignment={assignment}
              pauseAssignmentAction={pauseAssignmentAction}
              resumeAssignmentAction={resumeAssignmentAction}
            />
          </div>
        }
      />
      <main className="content stack screen-fit digital-worker-progress-screen">
        <section className="detail-grid digital-worker-detail-grid">
          <LeadInformation assignment={assignment} />
          <WorkerActivityCard assignment={assignment} />
        </section>
      </main>
    </>
  );
}

function AssignmentStatusAction({
  assignment,
  pauseAssignmentAction,
  resumeAssignmentAction
}: {
  assignment: DigitalWorkerAssignmentDetail;
  pauseAssignmentAction: FormAction;
  resumeAssignmentAction: FormAction;
}) {
  if (assignment.status === "active") {
    return (
      <form action={pauseAssignmentAction}>
        <input name="assignmentId" type="hidden" value={assignment.assignmentId} />
        <input name="leadId" type="hidden" value={assignment.leadId} />
        <Button type="submit" variant="secondary">
          <Pause size={15} /> Pause
        </Button>
      </form>
    );
  }

  if (assignment.status === "paused") {
    return (
      <form action={resumeAssignmentAction}>
        <input name="assignmentId" type="hidden" value={assignment.assignmentId} />
        <input name="leadId" type="hidden" value={assignment.leadId} />
        <Button type="submit" variant="primary">
          <Play size={15} /> Resume
        </Button>
      </form>
    );
  }

  return (
    <span className="filter-chip active">
      {assignment.status === "completed" ? "Completed" : "Failed"}
    </span>
  );
}

function WorkerActivityCard({ assignment }: { assignment: DigitalWorkerAssignmentDetail }) {
  return (
    <div className="surface-card worker-phase-card p-5" aria-label="Worker activity">
      <div className="flex min-w-0 flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <span className="icon-tile digital-worker-avatar" aria-hidden="true">
            <Bot size={18} />
          </span>
          <div className="min-w-0">
            <h2 className="section-title">Worker activity</h2>
            <p className="mt-1 text-xs font-semibold text-[var(--ink-600)]">
              Phase progress with the communication tied to each step.
            </p>
          </div>
        </div>
        <Link className="button purple small" href={routes.digitalWorkerAuditLog(assignment.assignmentId)}>
          <ExternalLink size={14} /> Audit Log
        </Link>
      </div>
      <VerticalWorkerTimeline assignment={assignment} />
    </div>
  );
}

function VerticalWorkerTimeline({ assignment }: { assignment: DigitalWorkerAssignmentDetail }) {
  return (
    <ol className="worker-phase-timeline">
      {assignment.steps.map((step, index) => {
        const isLast = index === assignment.steps.length - 1;
        const communication = communicationForStep(assignment, step.name, index);

        return (
          <li key={`${step.name}-${index}`} className={`worker-phase-step ${step.status}`}>
            <span className="worker-phase-node" aria-hidden="true">
              <StatusDot status={step.status} />
              {!isLast && <span className={`worker-phase-connector ${step.status === "done" ? "done" : ""}`} />}
            </span>
            <span className="worker-phase-content">
              <span className="flex min-w-0 items-baseline justify-between gap-3">
                <strong>{step.name}</strong>
                {step.duration && <span className="mono text-[10px] text-[var(--ink-400)]">{step.duration}</span>}
              </span>
              <span>{step.summary}</span>
              {step.chips && step.chips.length > 0 && (
                <span className="worker-phase-chips">
                  {step.chips.slice(0, 3).map((chip) => (
                    <span key={chip} className="source-chip border-solid text-[10.5px]">
                      {chip}
                    </span>
                  ))}
                </span>
              )}
              <StepCommunicationPreview communication={communication} />
            </span>
          </li>
        );
      })}
    </ol>
  );
}

function StatusDot({ status }: { status: DigitalWorkerStepStatus }) {
  if (status === "done") {
    return (
      <span className="worker-phase-dot done">
        <Check size={12} strokeWidth={3} />
      </span>
    );
  }

  return <span className={`worker-phase-dot ${status}`} />;
}

function StepCommunicationPreview({ communication }: { communication: TimelineEmail | undefined }) {
  if (!communication) {
    return null;
  }

  return (
    <article className="worker-step-communication" tabIndex={0}>
      <span className="mono">{communication.label}</span>
      <strong>{communication.subject}</strong>
      <p>{communication.body}</p>
      <div className="worker-step-popover" role="tooltip">
        <span className="mono">{communication.label}</span>
        <strong>{communication.subject}</strong>
        <p>{communication.body}</p>
      </div>
    </article>
  );
}

function LeadInformation({ assignment }: { assignment: DigitalWorkerAssignmentRow }) {
  return (
    <div className="surface-card lead-information-card p-5">
      <div className="flex min-w-0 flex-wrap items-center justify-between gap-3">
        <h2 className="section-title">Lead Information</h2>
        <Link className="button purple small" href={routes.leadDetail(assignment.leadId)}>
          <ExternalLink size={14} /> View lead
        </Link>
      </div>
      <dl className="mt-4 grid gap-4 sm:grid-cols-2">
        <InfoField label="Score / Tier" value={`${assignment.score} · ${assignment.tier}`} detail="Agent-generated priority" />
        <InfoField label="Contact" value={assignment.leadName} detail={assignment.leadRole} />
        <InfoField label="Email" value={assignment.email} detail="Primary lead email" />
        <InfoField label="Company" value={assignment.company} detail={formatUnits(assignment.units)} />
        <InfoField label="Market" value={assignment.market} detail={assignment.summary} />
      </dl>
      <div className="mt-5 grid grid-cols-2 gap-3 border-t border-[var(--border)] pt-5 sm:grid-cols-4">
        {assignment.marketSignals.map((signal) => (
          <div key={signal.label}>
            <span className="mono block text-[10px] uppercase text-[var(--ink-400)]">{signal.label}</span>
            <strong className="mono text-lg">{signal.value}</strong>
          </div>
        ))}
      </div>
      <div className="mt-5 border-t border-[var(--border)] pt-5">
        <h3 className="mono text-[10px] font-bold uppercase text-[var(--ink-400)]">Helpful context</h3>
        <ul className="mt-3 grid gap-2 text-sm leading-6 text-[var(--ink-600)]">
          {assignment.talkingPoints.slice(0, 3).map((point, index) => (
            <li key={`${point}-${index}`}>› {point}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function InfoField({ label, value, detail }: MetadataCardProps & { detail: string }) {
  return (
    <div className="lead-field">
      <dt className="mono text-[10px] font-bold uppercase text-[var(--ink-400)]">{label}</dt>
      <dd className="mt-1 text-sm font-bold">{value}</dd>
      <dd className="mt-1 text-xs font-semibold text-[var(--ink-600)]">{detail}</dd>
    </div>
  );
}

function formatUnits(units: number | null | undefined) {
  return units ? `${units.toLocaleString()} units` : "Units unavailable";
}

function titleize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace("Sdr", "SDR");
}
