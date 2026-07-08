"use client";

import { AlertTriangle, Ban, ChevronDown, ChevronLeft, Copy, ExternalLink, Inbox, Plus, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { KnowledgeGraph } from "@/components/features/leads/KnowledgeGraph";
import { Button } from "@/components/ui/Button";
import { EditableDraft } from "@/components/ui/EditableDraft";
import { PageHeader } from "@/components/ui/PageHeader";
import { SourceChip } from "@/components/ui/SourceChip";
import { TierBadge } from "@/components/ui/TierBadge";
import { Toast } from "@/components/ui/Toast";
import { digitalWorkerPreviewId } from "@/lib/fixtures/digital-workforce";
import { routes } from "@/lib/constants/routes";
import type { FixtureLead } from "@/types/lead";

interface Props {
  lead: FixtureLead;
}

interface FieldProps {
  label: string;
  value: string;
  detail: string;
}

export function LeadDetailView({ lead }: Props) {
  const failed = lead.gates.status === "failed";
  const [toast, setToast] = useState<string | null>(null);

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 2200);
  }

  return (
    <>
      <PageHeader
        title={lead.name}
        subtitle={`${lead.role} · ${lead.company} · ${lead.market}`}
        actions={
          <div className="flex gap-2">
            <Link className="button secondary" href={routes.leads}>
              <ChevronLeft size={16} /> Back
            </Link>
            {!failed && (
              <Link className="button primary" href={routes.digitalWorkerProgress(digitalWorkerPreviewId(lead.id))}>
                <Plus size={16} /> Assign Digital Worker
              </Link>
            )}
          </div>
        }
      />
      <main className="content stack">
        <Toast message={toast} />
        <div className="flex items-center gap-3">
          <TierBadge tier={lead.score.tier} />
          <span className="mono text-sm font-semibold">{lead.score.total}</span>
          <span className="text-sm text-[var(--ink-600)]">{lead.score.whyLine}</span>
        </div>
        {failed ? <GateFailedLead lead={lead} /> : <WorkableLeadDetail lead={lead} showToast={showToast} />}
      </main>
    </>
  );
}

function GateFailedLead({ lead }: Props) {
  return (
    <section className="detail-grid">
      <div className="stack">
        <div className="surface-card danger-panel p-5">
          <h2 className="section-title danger-title">
            <AlertTriangle size={16} /> Hard gates failed — do not work this lead
          </h2>
          <ul className="mt-4 grid gap-3 text-sm font-semibold text-[var(--danger-text)]">
            {lead.flags.map((flag, index) => (
              <li key={`${flag}-${index}`} className="gate-failure-item">
                <Ban size={15} />
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="surface-card p-5">
          <h2 className="section-title">Why flags matter</h2>
          <p className="mt-3 text-sm leading-6 text-[var(--ink-600)]">
            Signal keeps low-confidence records out of the outreach workflow so reps do not spend time on unverifiable
            accounts or risk sending to contacts without a trustworthy company signal.
          </p>
        </div>
      </div>
      <div className="surface-card flex min-h-80 flex-col items-center justify-center p-8 text-center">
        <span className="empty-icon">
          <Inbox size={24} />
        </span>
        <h2 className="text-lg font-bold">No draft generated</h2>
        <p className="mt-2 max-w-sm text-sm leading-6 text-[var(--ink-600)]">
          Signal suppresses outreach when required lead-quality gates fail.
        </p>
        <div className="mt-5 flex gap-2">
          <button className="button secondary" type="button">
            Dismiss lead
          </button>
          <button className="button secondary" type="button">
            Verify manually
          </button>
        </div>
      </div>
    </section>
  );
}

function WorkableLeadDetail({ lead, showToast }: Props & { showToast: (message: string) => void }) {
  const [subject, setSubject] = useState(lead.draft?.subject ?? "");
  const [body, setBody] = useState(lead.draft?.body ?? "");
  const relatedItems = lead.related.filter(isVisibleRelatedItem);
  const graphLead = { ...lead, related: relatedItems };
  const graphWarnings = lead.knowledgeGraph?.warnings ?? [];
  const hasGraphNotes = relatedItems.length > 0 || graphWarnings.length > 0;

  async function copyDraft() {
    await navigator.clipboard.writeText(`${subject}\n\n${body}`);
    showToast(`Draft copied for ${lead.name}`);
  }

  return (
    <section className="detail-grid lead-detail-layout">
      <div className="lead-detail-column" aria-label="Lead detail left column">
        <div className="surface-card p-5">
          <h2 className="section-title">Lead and enrichment</h2>
          <dl className="mt-4 grid gap-4 sm:grid-cols-2">
            <Field label="Contact" value={lead.email} detail="Corporate domain · valid MX" />
            <Field label="Seniority" value={lead.role} detail="Fit signal included" />
            <Field label="Company" value={lead.company} detail={`${lead.units?.toLocaleString()} units`} />
            <Field label="Property" value={lead.market} detail="Public data resolved" />
          </dl>
          <div className="mt-5 grid grid-cols-2 gap-3 border-t border-[var(--border)] pt-5 sm:grid-cols-4">
            {lead.marketSignals.map((signal) => (
              <div key={signal.label}>
                <span className="mono block text-[10px] uppercase text-[var(--ink-400)]">{signal.label}</span>
                <strong className="mono text-lg">{signal.value}</strong>
              </div>
            ))}
          </div>
        </div>
        <div className="surface-card lead-detail-fill-card lead-detail-knowledge-card p-5">
          <div className="flex items-center justify-between">
            <h2 className="section-title">Knowledge graph</h2>
            <span className="filter-chip active">{relatedItems.length} related</span>
          </div>
          <KnowledgeGraph lead={graphLead} />
          {hasGraphNotes && (
            <details className="graph-related-accordion">
              <summary>
                <span className="eyebrow">Related information</span>
                <ChevronDown aria-hidden="true" size={15} />
              </summary>
              <div className="related-list">
                {relatedItems.map((item) => (
                  <span key={item.id} className="related-list-item">
                    <strong>{item.label}</strong>
                    <span>{item.reason}</span>
                  </span>
                ))}
                {graphWarnings.map((warning) => (
                  <span key={warning} className="related-list-item">
                    {warning}
                  </span>
                ))}
              </div>
            </details>
          )}
        </div>
      </div>
      <div className="lead-detail-column" aria-label="Lead detail right column">
        <div className="surface-card p-5">
          <h2 className="section-title">Sales insights</h2>
          <p className="mt-2 text-xs font-semibold leading-5 text-[var(--ink-600)]">
            Public-data signals for prioritizing this inbound lead and tailoring outreach.
          </p>
          <ul className="mt-4 grid gap-3 text-sm leading-6">
            {lead.talkingPoints.map((point, index) => (
              <li key={`${point}-${index}`}>› {point}</li>
            ))}
          </ul>
        </div>
        <div className="surface-card lead-detail-fill-card lead-detail-draft-card p-5">
          <div className="flex min-w-0 flex-wrap items-center justify-between gap-3">
            <h2 className="section-title">Drafted email</h2>
          </div>
          <div className="mt-4 grid gap-2 border-b border-[var(--border)] pb-4 text-sm">
            <span className="min-w-0 overflow-wrap-anywhere">
              <strong>From:</strong> You · Signal SDR
            </span>
            <span className="min-w-0 overflow-wrap-anywhere">
              <strong>To:</strong> {lead.email}
            </span>
          </div>
          <EditableDraft
            subject={subject}
            body={body}
            onSubjectChange={setSubject}
            onBodyChange={setBody}
            bodyRows={8}
          />
          <details className="draft-sources-accordion">
            <summary>
              <span className="eyebrow">Sources</span>
              <ChevronDown aria-hidden="true" size={15} />
            </summary>
            <div className="mt-2 flex flex-wrap gap-2">
              {lead.draft?.sources.map((source) => (
                <SourceChip key={`${source.source}-${source.label}`} source={source} />
              ))}
            </div>
          </details>
          <div className="mt-auto flex justify-between pt-5">
            <Button disabled title="Draft regeneration requires a backend drafting endpoint">
              <RefreshCw size={15} /> Regenerate
            </Button>
            <div className="flex gap-2">
              <Button onClick={() => void copyDraft()}>
                <Copy size={15} /> Copy
              </Button>
              <Link className="button primary" href={routes.digitalWorkerProgress(digitalWorkerPreviewId(lead.id))}>
                <ExternalLink size={15} /> Open Digital Workforce
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Field({ label, value, detail }: FieldProps) {
  return (
    <div className="lead-field">
      <dt className="mono text-[10px] font-bold uppercase text-[var(--ink-400)]">{label}</dt>
      <dd className="mt-1 text-sm font-bold">{value}</dd>
      <dd className="mt-1 text-xs font-semibold text-[var(--ink-600)]">{detail}</dd>
    </div>
  );
}

function isVisibleRelatedItem(item: FixtureLead["related"][number]) {
  const combinedText = `${item.label} ${item.reason}`.toLowerCase();
  return !["seeded inbound history", "fixture history", "fixture"].some((hiddenText) => combinedText.includes(hiddenText));
}
