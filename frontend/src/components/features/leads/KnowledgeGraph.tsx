"use client";

import { Background, ReactFlow, type Edge, type Node } from "@xyflow/react";

import type { FixtureLead, KnowledgeGraphNodeDto } from "@/types/lead";

interface Props {
  lead: FixtureLead;
}

export function KnowledgeGraph({ lead }: Props) {
  if (lead.knowledgeGraph && lead.knowledgeGraph.nodes.length === 0) {
    return (
      <div className="knowledge-graph flex items-center justify-center text-sm font-semibold text-[var(--ink-600)]">
        No graph context available.
      </div>
    );
  }

  const nodes: Node[] = lead.knowledgeGraph
    ? lead.knowledgeGraph.nodes.map((graphNode, index) => nodeFromDto(graphNode, index))
    : fallbackNodes(lead);
  const edges: Edge[] = lead.knowledgeGraph
    ? lead.knowledgeGraph.edges.map((graphEdge) => ({
        id: graphEdge.id,
        source: graphEdge.source,
        target: graphEdge.target,
        label: graphEdge.relationship,
        animated: false,
        style: { stroke: "var(--graph-edge)", strokeWidth: 2 }
      }))
    : fallbackEdges();

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

function node(
  id: string,
  label: string,
  x: number,
  y: number,
  className = "graph-node-context"
): Node {
  return {
    id,
    position: { x, y },
    data: { label },
    className
  };
}

function nodeFromDto(graphNode: KnowledgeGraphNodeDto, index: number): Node {
  const position = graphPosition(graphNode, index);
  return node(graphNode.id, graphNode.label, position.x, position.y, classForKind(graphNode.kind));
}

function graphPosition(graphNode: KnowledgeGraphNodeDto, index: number) {
  const relatedOffset = Math.max(0, index - 6);
  const byKind = {
    lead: { x: graphNode.subtitle === "Related inbound lead" ? 370 : 175, y: graphNode.subtitle === "Related inbound lead" ? 176 + relatedOffset * 34 : 88 },
    contact: { x: 175, y: 16 },
    company: { x: 350, y: 16 },
    property: { x: 0, y: 88 },
    market: { x: 0, y: 176 },
    source_fact: { x: 350, y: 98 + relatedOffset * 28 },
    trigger: { x: 175, y: 176 }
  };
  return byKind[graphNode.kind];
}

function classForKind(kind: KnowledgeGraphNodeDto["kind"]) {
  return kind === "lead" || kind === "contact" ? "graph-node-contact" : "graph-node-context";
}

function fallbackNodes(lead: FixtureLead): Node[] {
  return [
    node("contact", lead.name, 170, 88, "graph-node-contact"),
    node("company", lead.company, 170, 0),
    node("market", lead.market, 0, 88),
    node("property", "Property context", 340, 88),
    node("related", `${lead.related.length || 0} related`, 170, 176)
  ];
}

function fallbackEdges(): Edge[] {
  return [
    edge("contact", "company"),
    edge("contact", "market"),
    edge("contact", "property"),
    edge("contact", "related")
  ];
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
