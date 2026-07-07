"use client";

import { Background, ReactFlow, type Edge, type Node } from "@xyflow/react";

import type { FixtureLead } from "@/types/lead";

interface Props {
  lead: FixtureLead;
}

export function KnowledgeGraph({ lead }: Props) {
  const nodes: Node[] = [
    node("contact", lead.name, 170, 88, "graph-node-contact"),
    node("company", lead.company, 170, 0),
    node("market", lead.market, 0, 88),
    node("property", "Property context", 340, 88),
    node("related", `${lead.related.length || 0} related`, 170, 176)
  ];
  const edges: Edge[] = [
    edge("contact", "company"),
    edge("contact", "market"),
    edge("contact", "property"),
    edge("contact", "related")
  ];

  return (
    <div className="knowledge-graph" aria-label="Lead knowledge graph">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        panOnDrag={false}
        zoomOnScroll={false}
        zoomOnPinch={false}
        preventScrolling={false}
      >
        <Background color="var(--graph-edge)" gap={18} />
      </ReactFlow>
    </div>
  );
}

function node(id: string, label: string, x: number, y: number, className = "graph-node-context"): Node {
  return {
    id,
    position: { x, y },
    data: { label },
    className
  };
}

function edge(source: string, target: string): Edge {
  return {
    id: `${source}-${target}`,
    source,
    target,
    animated: false,
    style: { stroke: "var(--graph-edge)", strokeWidth: 2 }
  };
}
