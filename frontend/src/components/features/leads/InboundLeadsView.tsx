import { ChevronRight, Copy, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { Flag } from "@/components/ui/Flag";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { ScoreMeter } from "@/components/ui/ScoreMeter";
import { TierBadge } from "@/components/ui/TierBadge";
import { routes } from "@/lib/constants/routes";
import { cn } from "@/lib/utils/cn";
import type { FixtureLead } from "@/types/lead";

interface Props {
  leads: FixtureLead[];
}

export function InboundLeadsView({ leads }: Props) {
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
            <span key={chip} className={cn("filter-chip", index === 0 && "active")}>
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
            {leads.map((lead) => (
              <Link
                key={lead.id}
                href={routes.leadDetail(lead.id)}
                className={cn(
                  "table-row lead-grid",
                  lead.score.tier === "A" && "tier-a-row",
                  lead.gates.status === "failed" && "dimmed"
                )}
              >
                <TierBadge tier={lead.score.tier} />
                <span>
                  <strong className="block text-sm">{lead.name}</strong>
                  <span className="text-xs font-semibold text-[var(--ink-600)]">{lead.role}</span>
                </span>
                <span className="text-sm font-semibold text-[var(--ink-500)]">{lead.company}</span>
                <span className="text-sm">{lead.market}</span>
                <span className="mono text-sm">{lead.units ? `${Math.round(lead.units / 1000)}k` : "-"}</span>
                <ScoreMeter score={lead.score.total} tier={lead.score.tier} />
                <span className="text-sm text-[var(--ink-600)]">{lead.score.whyLine}</span>
                <span>
                  {lead.gates.status === "failed" ? (
                    <Flag>Review flags</Flag>
                  ) : (
                    <span className="button secondary small">
                      <Copy aria-hidden="true" size={14} /> Copy draft
                    </span>
                  )}
                </span>
                <ChevronRight
                  size={18}
                  color={lead.gates.status === "failed" ? "var(--muted-chev)" : "var(--ink-400)"}
                />
              </Link>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
