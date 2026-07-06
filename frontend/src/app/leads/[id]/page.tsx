import { AlertTriangle, ChevronLeft, Copy, Download, MailX, Plus, RefreshCw } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { PageHeader } from "@/components/ui/PageHeader";
import { ScoreMeter } from "@/components/ui/ScoreMeter";
import { SourceChip } from "@/components/ui/SourceChip";
import { TierBadge } from "@/components/ui/TierBadge";
import { getLead } from "@/lib/fixtures/leads";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function LeadDetailPage({ params }: Props) {
  const { id } = await params;
  const lead = getLead(id);
  if (!lead) {
    notFound();
  }

  const failed = lead.gates.status === "failed";
  const draft = lead.draft;
  const draftNeedsReview = draft?.review_status === "needs_review";

  return (
    <>
      <PageHeader
        title={lead.name}
        subtitle={`${lead.role} · ${lead.company} · ${lead.market}`}
        actions={
          <div className="flex gap-2">
            <Link className="button secondary" href="/leads">
              <ChevronLeft size={16} /> Back
            </Link>
            {!failed && (
              <button className="button primary" type="button">
                <Plus size={16} /> Assign agent
              </button>
            )}
          </div>
        }
      />
      <main className="content stack-lg">
        <div className="flex flex-wrap items-center gap-3">
          <TierBadge tier={lead.score.tier} />
          <ScoreMeter score={lead.score.total} tier={lead.score.tier} />
          <span className="text-sm text-muted">{lead.score.whyLine}</span>
        </div>
        {failed ? (
          <section className="detail-grid">
            <div className="stack">
              <div className="surface-card danger flat p-5">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="text-danger" size={18} />
                  <h2 className="section-title text-danger">
                    Hard gates failed - do not work this lead
                  </h2>
                </div>
                <ul className="mt-4 grid gap-3 text-sm font-semibold">
                  {lead.flags.map((flag, index) => (
                    <li key={flag} className="flex gap-2">
                      <span className={index === 2 ? "text-warning" : "text-danger"}>
                        {index === 2 ? "!" : "x"}
                      </span>
                      <span>{flag}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="surface-card flat p-5">
                <div className="eyebrow">Why flags matter</div>
                <p className="mt-3 text-sm leading-6 text-subtle">
                  Telling a rep what not to work is part of Signal value. A draft is intentionally withheld
                  when lead quality gates fail.
                </p>
              </div>
            </div>
            <div className="surface-card flex min-h-80 flex-col items-center justify-center p-8 text-center">
              <div className="empty-icon mb-4">
                <MailX size={26} />
              </div>
              <h2 className="text-lg font-bold">No draft generated</h2>
              <p className="mt-2 max-w-sm text-sm leading-6 text-muted">
                Signal suppresses outreach for gate-failed leads. Verify the contact manually or dismiss it
                to clear it from the queue.
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
        ) : (
          <section className="detail-grid">
            <div className="stack">
              <div className="surface-card p-5">
                <h2 className="section-title">Lead and enrichment</h2>
                <dl className="field-grid">
                  <Field label="Contact" value={lead.email} detail="Corporate domain · valid MX" />
                  <Field label="Seniority" value={lead.role} detail="Fit signal included" />
                  <Field label="Company" value={lead.company} detail={`${lead.units?.toLocaleString()} units`} />
                  <Field label="Property" value={lead.market} detail="Public data resolved" />
                </dl>
                <div className="market-signals-grid">
                  {lead.marketSignals.map((signal) => (
                    <div key={signal.label}>
                      <span className="eyebrow block">{signal.label}</span>
                      <strong className="mono text-lg text-success">{signal.value}</strong>
                    </div>
                  ))}
                </div>
              </div>
              <div className="surface-card p-5">
                <h2 className="section-title">Talking points</h2>
                <ul className="mt-4 grid gap-3 text-sm leading-6">
                  {lead.talkingPoints.map((point) => (
                    <li key={point} className="flex gap-2">
                      <span className="font-bold text-success">&gt;</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="surface-card p-5">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="section-title">Knowledge graph</h2>
                  <span className="status-pill">{lead.related.length} related</span>
                </div>
                <div className="graph-section-grid">
                  <div className="graph-preview" aria-label="Knowledge graph preview">
                    <span className="graph-node primary">Contact</span>
                    <span className="graph-node north">Company</span>
                    <span className="graph-node east">Market</span>
                    <span className="graph-node south">Property</span>
                    <span className="graph-node west">Inbound</span>
                  </div>
                  <div>
                    <h3 className="eyebrow">Related leads</h3>
                    <div className="related-list">
                      {lead.related.length ? (
                        lead.related.map((item) => (
                          <div key={`${item.label}-${item.reason}`} className="related-card">
                            <strong className="block">{item.label}</strong>
                            <span>{item.reason}</span>
                          </div>
                        ))
                      ) : (
                        <span>No related leads in fixture history.</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {draft ? (
              <div className="surface-card flex flex-col p-5">
                <div className="flex items-center justify-between">
                  <h2 className="section-title">Drafted email</h2>
                  <span className="status-pill">
                    {draft.review_status === "needs_review"
                      ? "Review and copy"
                      : draft.review_status === "copied"
                        ? "Copied"
                        : "Exported"}
                  </span>
                </div>
                <div className="draft-meta">
                  <span><strong>To:</strong> {lead.email}</span>
                  <span><strong>Subject:</strong> {draft.subject}</span>
                </div>
                <pre className="draft-body mt-4">
                  {draft.body}
                </pre>
                <div className="mt-4 flex flex-wrap gap-2">
                  {draft.sources.map((source) => (
                    <SourceChip key={`${source.source}-${source.label}`} source={source} />
                  ))}
                </div>
                {draftNeedsReview && (
                  <div className="mt-auto flex justify-between pt-5">
                    <button className="button secondary" type="button"><RefreshCw size={15} /> Regenerate</button>
                    <div className="flex gap-2">
                      <button className="button secondary" type="button"><Copy size={15} /> Copy</button>
                      <button className="button primary" type="button"><Download size={15} /> Export</button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="surface-card flex min-h-80 flex-col items-center justify-center p-8 text-center">
                <div className="empty-icon mb-4">
                  <MailX size={26} />
                </div>
                <h2 className="text-lg font-bold">Draft pending</h2>
                <p className="mt-2 max-w-sm text-sm leading-6 text-muted">
                  Signal has not produced a draft for this lead yet. Copy and export controls appear only after
                  draft eligibility is complete.
                </p>
              </div>
            )}
          </section>
        )}
      </main>
    </>
  );
}

function Field({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div>
      <dt className="eyebrow">{label}</dt>
      <dd className="mt-1 text-sm font-bold">{value}</dd>
      <dd className="mt-1 text-xs font-semibold text-muted">{detail}</dd>
    </div>
  );
}
