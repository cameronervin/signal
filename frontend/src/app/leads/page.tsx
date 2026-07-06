import { ChevronRight, Copy, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { Flag } from "@/components/ui/Flag";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { ScoreMeter } from "@/components/ui/ScoreMeter";
import { TierBadge } from "@/components/ui/TierBadge";
import { leads } from "@/lib/fixtures/leads";

export default function LeadsPage() {
  const sortedLeads = [...leads].sort((a, b) => {
    const tierOrder = { A: 0, B: 1, C: 2 };
    return tierOrder[a.score.tier] - tierOrder[b.score.tier] || b.score.total - a.score.total;
  });
  const tierACount = leads.filter((lead) => lead.score.tier === "A").length;

  return (
    <>
      <PageHeader
        title="Inbound Leads"
        subtitle={`${leads.length} open · sorted by tier`}
        actions={
          <div className="flex gap-2">
            <button className="button secondary" type="button">
              <SlidersHorizontal size={16} /> Filter
            </button>
            <SearchInput label="Search inbound leads" placeholder="Search leads..." />
          </div>
        }
      />
      <main className="content stack-lg">
        <div className="flex flex-wrap gap-2">
          {[`Tier A · ${tierACount}`, "Corporate email", "Unassigned", "+ Add filter"].map((chip, index) => (
            <span key={chip} className={`filter-chip ${index === 0 ? "active" : ""}`}>
              {chip}
            </span>
          ))}
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
            <span>Draft</span>
            <span />
          </div>
          <div className="table-body">
            {sortedLeads.map((lead) => (
              <Link
                key={lead.id}
                href={`/leads/${lead.id}`}
                className={`table-row lead-grid ${lead.score.tier === "A" ? "tier-a-row" : ""} ${
                  lead.gates.status === "failed" ? "dimmed" : ""
                }`}
              >
                <TierBadge tier={lead.score.tier} />
                <span>
                  <strong className="block text-sm">{lead.name}</strong>
                  <span className="text-xs font-semibold text-muted">{lead.role}</span>
                </span>
                <span className="text-sm font-semibold text-subtle">{lead.company}</span>
                <span className="text-sm">{lead.market}</span>
                <span className="mono text-sm">{lead.units ? `${Math.round(lead.units / 1000)}k` : "-"}</span>
                <ScoreMeter score={lead.score.total} tier={lead.score.tier} />
                <span className="text-sm text-muted">{lead.score.whyLine}</span>
                <span>
                  {lead.gates.status === "failed" ? (
                    <Flag>Review flags</Flag>
                  ) : lead.draft ? (
                    <span className="button secondary small">
                      <Copy aria-hidden="true" size={14} /> Copy draft
                    </span>
                  ) : (
                    <span className="status-pill muted">Draft pending</span>
                  )}
                </span>
                <ChevronRight className={lead.gates.status === "failed" ? "chevron-muted" : "chevron-soft"} size={18} />
              </Link>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
