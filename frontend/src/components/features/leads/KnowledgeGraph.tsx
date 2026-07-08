"use client";

import { useEffect, useMemo } from "react";
import { Background, Controls, ReactFlow, type Edge, type Node, useEdgesState, useNodesState } from "@xyflow/react";

import type { FixtureLead, KnowledgeGraphNodeDto } from "@/types/lead";

interface Props {
  lead: FixtureLead;
}

export function KnowledgeGraph({ lead }: Props) {
  const { company: leadCompany, market: leadMarket, name: leadName } = lead;
  const graph = lead.knowledgeGraph;
  const graphNodes = graph?.nodes ?? null;
  const graphEdges = graph?.edges ?? null;
  const relatedCount = lead.related.length;

  const initialNodes = useMemo<Node[]>(
    () =>
      graphNodes
        ? graphNodes.map((graphNode, index) => nodeFromDto(graphNode, index))
        : fallbackNodes(leadName, leadCompany, leadMarket, relatedCount),
    [graphNodes, leadCompany, leadMarket, leadName, relatedCount]
  );
  const initialEdges = useMemo<Edge[]>(
    () =>
      graphEdges
        ? graphEdges.map((graphEdge) => ({
            id: graphEdge.id,
            source: graphEdge.source,
            target: graphEdge.target,
            label: graphEdge.relationship,
            animated: false,
            style: { stroke: "var(--graph-edge)", strokeWidth: 2 }
          }))
        : fallbackEdges(),
    [graphEdges]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialEdges, initialNodes, setEdges, setNodes]);

  if (graph && graph.nodes.length === 0) {
    return (
      <div className="knowledge-graph flex items-center justify-center text-sm font-semibold text-[var(--ink-600)]">
        No graph context available.
      </div>
    );
  }

  return (
    <div className="knowledge-graph" aria-label="Lead knowledge graph">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        nodesDraggable
        nodesConnectable={false}
        edgesReconnectable={false}
        elementsSelectable
        panOnDrag
        zoomOnScroll
        zoomOnPinch
      >
        <Controls showInteractive={false} />
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

function fallbackNodes(leadName: string, leadCompany: string, leadMarket: string, relatedCount: number): Node[] {
  return [
    node("contact", leadName, 170, 88, "graph-node-contact"),
    node("company", leadCompany, 170, 0),
    node("market", leadMarket, 0, 88),
    node("property", "Property context", 340, 88),
    node("related", `${relatedCount} related`, 170, 176)
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
