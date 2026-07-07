"use client";

import { ChevronRight, Copy, SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { FilterChip } from "@/components/ui/FilterChip";
import { Flag } from "@/components/ui/Flag";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { ScoreMeter } from "@/components/ui/ScoreMeter";
import { TierBadge } from "@/components/ui/TierBadge";
import { Toast } from "@/components/ui/Toast";
import { routes } from "@/lib/constants/routes";
import { cn } from "@/lib/utils/cn";
import type { FixtureLead } from "@/types/lead";

interface Props {
  leads: FixtureLead[];
}

export function InboundLeadsView({ leads }: Props) {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [tierAOnly, setTierAOnly] = useState(false);
  const [corporateOnly, setCorporateOnly] = useState(false);
  const [unassignedOnly, setUnassignedOnly] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const tierACount = leads.filter((lead) => lead.score.tier === "A").length;
  const filteredLeads = useMemo(
    () =>
      leads.filter((lead) => {
        const query = search.trim().toLowerCase();
        const matchesSearch =
          !query ||
          [lead.name, lead.role, lead.company, lead.market, lead.score.whyLine]
            .join(" ")
            .toLowerCase()
            .includes(query);
        const matchesTier = !tierAOnly || lead.score.tier === "A";
        const matchesCorporate = !corporateOnly || lead.gates.status === "passed";
        const matchesAssignment = !unassignedOnly || !lead.runId;

        return matchesSearch && matchesTier && matchesCorporate && matchesAssignment;
      }),
    [corporateOnly, leads, search, tierAOnly, unassignedOnly]
  );

  async function copyDraft(lead: FixtureLead) {
    if (!lead.draft) {
      return;
    }

    await navigator.clipboard.writeText(`${lead.draft.subject}\n\n${lead.draft.body}`);
    setToast(`Draft copied for ${lead.name}`);
    window.setTimeout(() => setToast(null), 2200);
  }

  function openLead(leadId: string) {
    router.push(routes.leadDetail(leadId));
  }

  return (
    <>
      <PageHeader
        title="Inbound Leads"
        subtitle={`${filteredLeads.length} open · sorted by tier`}
        actions={
          <div className="flex gap-2">
            <Button>
              <SlidersHorizontal size={16} /> Filter
            </Button>
            <SearchInput label="Search inbound leads" placeholder="Search leads..." value={search} onChange={setSearch} />
          </div>
        }
      />
      <main className="content stack-lg">
        <Toast message={toast} />
        <div className="flex flex-wrap gap-2">
          <FilterChip active={tierAOnly} onClick={() => setTierAOnly((active) => !active)}>
            Tier A · {tierACount}
          </FilterChip>
          <FilterChip active={corporateOnly} onClick={() => setCorporateOnly((active) => !active)}>
            Corporate email
          </FilterChip>
          <FilterChip active={unassignedOnly} onClick={() => setUnassignedOnly((active) => !active)}>
            Unassigned
          </FilterChip>
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
            {filteredLeads.map((lead) => (
              <div
                key={lead.id}
                role="link"
                tabIndex={0}
                className={cn(
                  "table-row lead-grid",
                  lead.score.tier === "A" && "tier-a-row",
                  lead.gates.status === "failed" && "dimmed"
                )}
                onClick={() => openLead(lead.id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    openLead(lead.id);
                  }
                }}
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
                    <Button
                      size="small"
                      onClick={(event) => {
                        event.stopPropagation();
                        void copyDraft(lead);
                      }}
                    >
                      <Copy aria-hidden="true" size={14} /> Copy draft
                    </Button>
                  )}
                </span>
                <ChevronRight
                  size={18}
                  color={lead.gates.status === "failed" ? "var(--muted-chev)" : "var(--ink-400)"}
                />
              </div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
