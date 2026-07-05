import type { SourceFact } from "@/types/lead";

interface Props {
  source: SourceFact;
}

export function SourceChip({ source }: Props) {
  return (
    <span className="source-chip">
      <span className="source-chip-label">{source.source}</span>
      {source.label}: {source.value}
    </span>
  );
}
