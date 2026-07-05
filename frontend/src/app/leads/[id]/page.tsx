import { ChevronLeft, Copy, RefreshCw, Send } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { PageHeader } from "@/components/ui/PageHeader";
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
            {!failed && <button className="button primary" type="button">Assign agent</button>}
          </div>
        }
      />
      <main className="content stack">
        <div className="flex items-center gap-3">
          <TierBadge tier={lead.score.tier} />
          <span className="mono text-sm font-semibold">{lead.score.total}</span>
          <span className="text-sm text-[var(--ink-600)]">{lead.score.whyLine}</span>
        </div>
        {failed ? (
          <section className="detail-grid">
            <div className="surface-card border-[var(--danger-border)] bg-[#FDF5F5] p-5">
              <h2 className="section-title text-[var(--danger-text)]">Hard gates failed</h2>
              <ul className="mt-4 grid gap-3 text-sm font-semibold text-[var(--danger-text)]">
                {lead.flags.map((flag) => (
                  <li key={flag}>x {flag}</li>
                ))}
              </ul>
            </div>
            <div className="surface-card flex min-h-80 flex-col items-center justify-center p-8 text-center">
              <h2 className="text-lg font-bold">No draft generated</h2>
              <p className="mt-2 max-w-sm text-sm leading-6 text-[var(--ink-600)]">
                Signal suppresses outreach when required lead-quality gates fail.
              </p>
              <div className="mt-5 flex gap-2">
                <button className="button secondary" type="button">Dismiss lead</button>
                <button className="button secondary" type="button">Verify manually</button>
              </div>
            </div>
          </section>
        ) : (
          <section className="detail-grid">
            <div className="stack">
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
              <div className="surface-card p-5">
                <h2 className="section-title">Talking points</h2>
                <ul className="mt-4 grid gap-3 text-sm leading-6">
                  {lead.talkingPoints.map((point) => (
                    <li key={point}>› {point}</li>
                  ))}
                </ul>
              </div>
              <div className="surface-card p-5">
                <h2 className="section-title">Knowledge graph</h2>
                <div className="mt-4 rounded-lg border border-[var(--border)] bg-[var(--surface-2)] p-4 text-sm text-[var(--ink-600)]">
                  Contact {"->"} Company {"->"} Property {"->"} Market. Related
                  context:
                  {lead.related.map((item) => ` ${item.reason}`).join("; ")}
                </div>
              </div>
            </div>
            <div className="surface-card flex flex-col p-5">
              <div className="flex items-center justify-between">
                <h2 className="section-title">Drafted email</h2>
                <span className="rounded-md bg-[var(--brand-tint)] px-2 py-1 text-xs font-bold text-[var(--brand-deep)]">
                  Review and send
                </span>
              </div>
              <div className="mt-4 grid gap-2 border-b border-[var(--border)] pb-4 text-sm">
                <span><strong>To:</strong> {lead.email}</span>
                <span><strong>Subject:</strong> {lead.draft?.subject}</span>
              </div>
              <pre className="mt-4 whitespace-pre-wrap rounded-lg bg-[var(--surface-2)] p-4 text-sm leading-6 text-[var(--ink-700)]">
                {lead.draft?.body}
              </pre>
              <div className="mt-4 flex flex-wrap gap-2">
                {lead.draft?.sources.map((source) => (
                  <span key={`${source.source}-${source.label}`} className="rounded-md border border-dashed border-[#C9BEF7] bg-[var(--brand-tint-2)] px-2 py-1 text-xs font-semibold text-[var(--brand-deep)]">
                    <span className="mono">{source.source}</span> {source.label}: {source.value}
                  </span>
                ))}
              </div>
              <div className="mt-auto flex justify-between pt-5">
                <button className="button secondary" type="button"><RefreshCw size={15} /> Regenerate</button>
                <div className="flex gap-2">
                  <button className="button secondary" type="button"><Copy size={15} /> Copy</button>
                  <button className="button primary" type="button"><Send size={15} /> Send</button>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>
    </>
  );
}

function Field({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div>
      <dt className="mono text-[10px] font-bold uppercase text-[var(--ink-400)]">{label}</dt>
      <dd className="mt-1 text-sm font-bold">{value}</dd>
      <dd className="mt-1 text-xs font-semibold text-[var(--ink-600)]">{detail}</dd>
    </div>
  );
}
