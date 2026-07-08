"use client";

import { Bot, ChevronLeft, ExternalLink } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { PipelineStepper } from "@/components/ui/PipelineStepper";
import { routes } from "@/lib/constants/routes";
import type { DigitalWorkerAssignmentPreview, DigitalWorkerProfile } from "@/types/digital-workforce";

interface Props {
  assignment: DigitalWorkerAssignmentPreview;
  worker: DigitalWorkerProfile;
}

interface MetadataCardProps {
  label: string;
  value: string;
}

export function DigitalWorkerProgressView({ assignment, worker }: Props) {
  return (
    <>
      <PageHeader
        title="SDR Digital Worker"
        subtitle={worker.displayName}
        actions={
          <div className="toolbar-row">
            <Link className="button secondary" href={routes.digitalWorkforce}>
              <ChevronLeft size={16} /> Back
            </Link>
            <Button disabled variant="primary" title="Digital worker assignment is not connected to the backend yet">
              Assign worker
            </Button>
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
      </main>
    </>
  );
}

function LeadInformation({ assignment }: { assignment: DigitalWorkerAssignmentPreview }) {
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
