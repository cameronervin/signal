"use client";

import { Bot, ChevronLeft, Clock, ExternalLink, Mail, Pause, Play } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { PipelineStepper } from "@/components/ui/PipelineStepper";
import { routes } from "@/lib/constants/routes";
import type {
  DigitalWorkerAssignmentDetail,
  DigitalWorkerAssignmentRow,
  DigitalWorkerFollowUpDto,
  DigitalWorkerGoalStateDto,
  DigitalWorkerMessageDto,
  DigitalWorkerProfile,
  DigitalWorkerRunDto
} from "@/types/digital-workforce";

type FormAction = (formData: FormData) => void | Promise<void>;

interface Props {
  assignment: DigitalWorkerAssignmentDetail;
  pauseAssignmentAction: FormAction;
  recordInboundEmailAction: FormAction;
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
  recordInboundEmailAction,
  resumeAssignmentAction,
  worker
}: Props) {
  return (
    <>
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
        <section className="detail-grid">
          <LeadInformation assignment={assignment} />
          <div className="surface-card p-5">
            <div className="flex items-center gap-3">
              <span className="icon-tile digital-worker-avatar">
                <Bot size={18} />
              </span>
              <div>
                <h2 className="section-title">Worker activity</h2>
                <p className="mt-1 text-xs font-semibold text-[var(--ink-600)]">
                  Worker updates appear here as the agent progresses.
                </p>
              </div>
            </div>
            <div className="mt-5">
              <PipelineStepper steps={assignment.steps} />
            </div>
          </div>
        </section>
        <section className="detail-grid">
          <SandboxMessages assignment={assignment} />
          <WorkerState assignment={assignment} recordInboundEmailAction={recordInboundEmailAction} />
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

function LeadInformation({ assignment }: { assignment: DigitalWorkerAssignmentRow }) {
  return (
    <div className="surface-card lead-information-card p-5">
      <div className="flex min-w-0 flex-wrap items-center justify-between gap-3">
        <h2 className="section-title">Lead Information</h2>
        <span className="mono review-score">
          {assignment.score} · {assignment.tier}
        </span>
      </div>
      <dl className="mt-4 grid gap-4 sm:grid-cols-2">
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
      <div className="review-actions">
        <Link className="button purple" href={routes.leadDetail(assignment.leadId)}>
          <ExternalLink size={15} /> View lead
        </Link>
      </div>
    </div>
  );
}

function SandboxMessages({ assignment }: { assignment: DigitalWorkerAssignmentDetail }) {
  return (
    <div className="surface-card p-5">
      <div className="flex items-center gap-3">
        <span className="icon-tile">
          <Mail size={17} />
        </span>
        <div>
          <h2 className="section-title">Sandbox email</h2>
          <p className="mt-1 text-xs font-semibold text-[var(--ink-600)]">
            Persisted sandbox messages for SDR check-ins.
          </p>
        </div>
      </div>
      <div className="mt-5 grid gap-3">
        {assignment.messages.map((message) => (
          <MessageItem key={message.message_id} message={message} />
        ))}
        {assignment.messages.length === 0 && (
          <p className="text-sm font-semibold text-[var(--ink-500)]">No sandbox messages have been persisted yet.</p>
        )}
      </div>
    </div>
  );
}

function WorkerState({
  assignment,
  recordInboundEmailAction
}: {
  assignment: DigitalWorkerAssignmentDetail;
  recordInboundEmailAction: FormAction;
}) {
  return (
    <div className="surface-card p-5">
      <div className="flex items-center gap-3">
        <span className="icon-tile">
          <Clock size={17} />
        </span>
        <div>
          <h2 className="section-title">Worker state</h2>
          <p className="mt-1 text-xs font-semibold text-[var(--ink-600)]">
            Goals, runs, follow-ups, and SDR-triggered sandbox replies.
          </p>
        </div>
      </div>
      <div className="mt-5 grid gap-5">
        <InboundEmailForm
          assignment={assignment}
          recordInboundEmailAction={recordInboundEmailAction}
        />
        <StateList title="Goals" items={assignment.goals} renderItem={(goal) => <GoalItem goal={goal} />} />
        <StateList
          title="Follow-ups"
          items={assignment.followUps}
          renderItem={(followUp) => <FollowUpItem followUp={followUp} />}
        />
        <StateList title="Runs" items={assignment.runs} renderItem={(run) => <RunItem run={run} />} />
        <StateList
          title="Activity"
          items={assignment.activityLog}
          renderItem={(activity) => <span className="text-sm font-semibold text-[var(--ink-600)]">{activity}</span>}
        />
      </div>
    </div>
  );
}

function InboundEmailForm({
  assignment,
  recordInboundEmailAction
}: {
  assignment: DigitalWorkerAssignmentDetail;
  recordInboundEmailAction: FormAction;
}) {
  if (assignment.status !== "active") {
    return (
      <div className="rounded-md border border-[var(--border)] p-4 text-sm font-semibold text-[var(--ink-600)]">
        Inbound sandbox email is available only while the assignment is active.
      </div>
    );
  }

  return (
    <form action={recordInboundEmailAction} className="grid gap-3 rounded-md border border-[var(--border)] p-4">
      <input name="assignmentId" type="hidden" value={assignment.assignmentId} />
      <input name="leadId" type="hidden" value={assignment.leadId} />
      <label className="grid gap-1 text-sm font-semibold">
        Subject
        <input
          className="rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm outline-none focus:border-[var(--purple)]"
          maxLength={240}
          name="subject"
          placeholder="Re: leasing follow-up"
          required
        />
      </label>
      <label className="grid gap-1 text-sm font-semibold">
        Sandbox reply
        <textarea
          className="min-h-24 rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm outline-none focus:border-[var(--purple)]"
          maxLength={12000}
          name="body"
          placeholder="Can we schedule a call next week?"
          required
        />
      </label>
      <Button size="small" type="submit" variant="primary">
        <Mail size={14} /> Record inbound email
      </Button>
    </form>
  );
}

function StateList<T>({
  items,
  renderItem,
  title
}: {
  items: T[];
  renderItem: (item: T) => ReactNode;
  title: string;
}) {
  return (
    <div>
      <h3 className="mono text-[10px] font-bold uppercase text-[var(--ink-400)]">{title}</h3>
      <div className="mt-3 grid gap-2">
        {items.map((item, index) => (
          <div key={`${title}-${index}`} className="rounded-md border border-[var(--border)] p-3">
            {renderItem(item)}
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-sm font-semibold text-[var(--ink-500)]">No {title.toLowerCase()} recorded yet.</p>
        )}
      </div>
    </div>
  );
}

function GoalItem({ goal }: { goal: DigitalWorkerGoalStateDto }) {
  return (
    <span className="grid gap-1 text-sm">
      <strong>{titleize(goal.goal_key)}</strong>
      <span className="text-[var(--ink-600)]">
        {titleize(goal.phase_key)} · {goal.status}
      </span>
      {goal.notes && <span className="text-[var(--ink-600)]">{goal.notes}</span>}
    </span>
  );
}

function MessageItem({ message }: { message: DigitalWorkerMessageDto }) {
  return (
    <article className="rounded-md border border-[var(--border)] p-3">
      <div className="flex min-w-0 flex-wrap items-center justify-between gap-2">
        <strong className="text-sm">{message.subject}</strong>
        <span className="mono text-[10px] uppercase text-[var(--ink-400)]">{message.direction}</span>
      </div>
      <p className="mt-2 overflow-wrap-anywhere text-sm leading-6 text-[var(--ink-600)]">{message.body}</p>
      {message.created_at && (
        <span className="mono mt-2 block text-[10px] text-[var(--ink-400)]">{formatDate(message.created_at)}</span>
      )}
    </article>
  );
}

function FollowUpItem({ followUp }: { followUp: DigitalWorkerFollowUpDto }) {
  return (
    <span className="grid gap-1 text-sm">
      <strong>{followUp.reason}</strong>
      <span className="text-[var(--ink-600)]">
        {followUp.status} · due {formatDate(followUp.due_at)}
      </span>
    </span>
  );
}

function RunItem({ run }: { run: DigitalWorkerRunDto }) {
  return (
    <span className="grid gap-1 text-sm">
      <strong>{titleize(run.trigger)}</strong>
      <span className="text-[var(--ink-600)]">
        {run.status} · {titleize(run.current_phase)}
      </span>
      {run.message && <span className="text-[var(--ink-600)]">{run.message}</span>}
    </span>
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

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function titleize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace("Sdr", "SDR");
}
