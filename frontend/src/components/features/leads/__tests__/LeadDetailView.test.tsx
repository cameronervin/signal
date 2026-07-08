import { fireEvent, render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";

import { KnowledgeGraph } from "@/components/features/leads/KnowledgeGraph";
import { LeadDetailView } from "@/components/features/leads/LeadDetailView";
import { digitalWorkerPreviewId } from "@/lib/fixtures/digital-workforce";
import { leads } from "@/lib/fixtures/leads";
import type { FixtureLead } from "@/types/lead";

type MockGraphNode = {
  id: string;
  data?: { label?: string };
  position?: { x: number; y: number };
};

type MockGraphEdge = {
  id: string;
  label?: string;
};

type MockNodeChange = {
  id: string;
  type: "position" | "select";
  position?: { x: number; y: number };
  selected?: boolean;
};

jest.mock("@xyflow/react", () => {
  const React = jest.requireActual("react") as typeof import("react");

  function applyNodeChanges(changes: MockNodeChange[], nodes: MockGraphNode[]) {
    return nodes.map((node) => {
      const change = changes.find((item) => item.id === node.id);
      if (!change) {
        return node;
      }
      if (change.type === "position") {
        return { ...node, position: change.position ?? node.position };
      }
      return node;
    });
  }

  return {
    Background: () => null,
    Controls: () => <div data-testid="graph-controls" />,
    ReactFlow: ({
      children,
      edges = [],
      edgesReconnectable,
      elementsSelectable,
      nodes = [],
      nodesConnectable,
      nodesDraggable,
      onNodesChange,
      panOnDrag,
      zoomOnPinch,
      zoomOnScroll
    }: {
      children: ReactNode;
      edges?: MockGraphEdge[];
      edgesReconnectable?: boolean;
      elementsSelectable?: boolean;
      nodes?: MockGraphNode[];
      nodesConnectable?: boolean;
      nodesDraggable?: boolean;
      onNodesChange?: (changes: MockNodeChange[]) => void;
      panOnDrag?: boolean;
      zoomOnPinch?: boolean;
      zoomOnScroll?: boolean;
    }) => (
      <div
        data-edges-reconnectable={String(edgesReconnectable)}
        data-elements-selectable={String(elementsSelectable)}
        data-has-on-nodes-change={String(Boolean(onNodesChange))}
        data-nodes-connectable={String(nodesConnectable)}
        data-nodes-draggable={String(nodesDraggable)}
        data-pan-on-drag={String(panOnDrag)}
        data-testid="knowledge-graph"
        data-zoom-on-pinch={String(zoomOnPinch)}
        data-zoom-on-scroll={String(zoomOnScroll)}
      >
        <button
          type="button"
          onClick={() => onNodesChange?.([{ id: nodes[0]?.id ?? "", type: "position", position: { x: 250, y: 260 } }])}
        >
          Move first graph node
        </button>
        {nodes.map((node) => (
          <span key={node.id} data-position={`${node.position?.x},${node.position?.y}`} data-testid={`graph-node-${node.id}`}>
            {node.data?.label}
          </span>
        ))}
        {edges.map((edge) => (
          <span key={edge.id} data-testid={`graph-edge-${edge.id}`}>
            {edge.label}
          </span>
        ))}
        {children}
      </div>
    ),
    useEdgesState: (initialEdges: MockGraphEdge[]) => {
      const [edges, setEdges] = React.useState(initialEdges);
      return [edges, setEdges, jest.fn()];
    },
    useNodesState: (initialNodes: MockGraphNode[]) => {
      const [nodes, setNodes] = React.useState(initialNodes);
      const onNodesChange = (changes: MockNodeChange[]) => {
        setNodes((currentNodes) => applyNodeChanges(changes, currentNodes));
      };
      return [nodes, setNodes, onNodesChange];
    }
  };
});

describe("LeadDetailView", () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined)
      }
    });
  });

  it("renders an editable draft with digital workforce handoff actions for workable leads", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(screen.getByDisplayValue("Improving leasing response in Austin")).toBeInTheDocument();
    expect(screen.queryByText("Review gate")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: /assign digital worker/i })).toHaveAttribute(
      "href",
      `/agents/${digitalWorkerPreviewId(lead!.id)}`
    );
    expect(screen.getByRole("link", { name: /open digital workforce/i })).toHaveAttribute(
      "href",
      `/agents/${digitalWorkerPreviewId(lead!.id)}`
    );
    expect(screen.queryByRole("link", { name: /^send$/i })).not.toBeInTheDocument();

    fireEvent.change(screen.getByDisplayValue("Improving leasing response in Austin"), {
      target: { value: "Updated subject" }
    });
    expect(screen.getByDisplayValue("Updated subject")).toBeInTheDocument();
  });

  it("places enrichment and graph in the left column and sales insights above the draft on the right", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(
      within(screen.getByLabelText("Lead detail left column"))
        .getAllByRole("heading")
        .map((heading) => heading.textContent)
    ).toEqual(["Lead and enrichment", "Knowledge graph"]);
    expect(
      within(screen.getByLabelText("Lead detail right column"))
        .getAllByRole("heading")
        .map((heading) => heading.textContent)
    ).toEqual(["Sales insights", "Drafted email"]);
    expect(
      screen.getByText("Public-data signals for prioritizing this inbound lead and tailoring outreach.")
    ).toBeInTheDocument();
  });

  it("renders an empty sales insights section without crashing", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={{ ...lead!, talkingPoints: [] }} />);

    const salesInsightsCard = screen.getByText("Sales insights").closest(".surface-card");
    expect(salesInsightsCard).toBeInTheDocument();
    expect(within(salesInsightsCard as HTMLElement).queryAllByRole("listitem")).toHaveLength(0);
  });

  it("keeps drafted email sources closed by default", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    const sourcesDisclosure = screen.getByText("Sources").closest("details");
    expect(sourcesDisclosure).toBeInTheDocument();
    expect(sourcesDisclosure).not.toHaveAttribute("open");
  });

  it("keeps knowledge graph related information closed by default", () => {
    const lead = withKnowledgeGraph({
      nodes: [
        {
          id: "lead_backend",
          kind: "lead",
          label: "Backend Contact",
          subtitle: "Current inbound lead",
          source_fact_ids: []
        }
      ],
      edges: [],
      sources: [],
      related_leads: [],
      warnings: ["Graph context warning"]
    });

    render(<LeadDetailView lead={lead} />);

    const relatedDisclosure = screen.getByText("Related information").closest("details");
    expect(relatedDisclosure).toBeInTheDocument();
    expect(relatedDisclosure).not.toHaveAttribute("open");
  });

  it("hides seeded related-history text from the knowledge graph notes", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(screen.queryByText("Related inbound")).not.toBeInTheDocument();
    expect(screen.queryByText("Same company appeared in fixture history")).not.toBeInTheDocument();
  });

  it("renders duplicate visible related rows without duplicate React keys", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();
    const consoleErrorSpy = jest.spyOn(console, "error").mockImplementation(() => undefined);

    try {
      render(
        <LeadDetailView
          lead={{
            ...lead!,
            related: [
              { id: "related:duplicate-one", label: "Related inbound", reason: "Shared source category." },
              { id: "related:duplicate-two", label: "Related inbound", reason: "Shared source category." }
            ]
          }}
        />
      );

      expect(screen.getAllByText("Related inbound")).toHaveLength(2);
      expect(screen.getAllByText("Shared source category.")).toHaveLength(2);
      expect(screen.queryByText("related:duplicate-one")).not.toBeInTheDocument();
      expect(screen.queryByText("related:duplicate-two")).not.toBeInTheDocument();
      expect(
        consoleErrorSpy.mock.calls.some((call) =>
          call.some((message) => String(message).includes("Encountered two children with the same key"))
        )
      ).toBe(false);
    } finally {
      consoleErrorSpy.mockRestore();
    }
  });

  it("suppresses drafts for gate-failed leads", () => {
    const lead = leads.find((item) => item.name === "Tom Whitaker");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(screen.getByText(/Hard gates failed/)).toBeInTheDocument();
    expect(screen.getByText("No draft generated")).toBeInTheDocument();
    expect(screen.queryByText("Drafted email")).not.toBeInTheDocument();
  });

  it("renders backend knowledge graph nodes and edges", () => {
    const lead = withKnowledgeGraph();

    render(<LeadDetailView lead={lead} />);

    expect(screen.getByTestId("graph-node-lead_backend")).toHaveTextContent("Backend Contact");
    expect(screen.getByTestId("graph-node-company_backend")).toHaveTextContent("Backend Company");
    expect(screen.getByTestId("graph-edge-edge_backend")).toHaveTextContent("WORKS_AT");
  });

  it("configures the knowledge graph for interactive read-only exploration", () => {
    const lead = withKnowledgeGraph();

    render(<KnowledgeGraph lead={lead} />);

    const graph = screen.getByTestId("knowledge-graph");
    expect(graph).toHaveAttribute("data-has-on-nodes-change", "true");
    expect(graph).toHaveAttribute("data-nodes-draggable", "true");
    expect(graph).toHaveAttribute("data-elements-selectable", "true");
    expect(graph).toHaveAttribute("data-pan-on-drag", "true");
    expect(graph).toHaveAttribute("data-zoom-on-scroll", "true");
    expect(graph).toHaveAttribute("data-zoom-on-pinch", "true");
    expect(graph).toHaveAttribute("data-nodes-connectable", "false");
    expect(graph).toHaveAttribute("data-edges-reconnectable", "false");
    expect(screen.getByTestId("graph-controls")).toBeInTheDocument();
  });

  it("updates node positions when React Flow reports a drag change", () => {
    const lead = withKnowledgeGraph();

    render(<KnowledgeGraph lead={lead} />);

    expect(screen.getByTestId("graph-node-lead_backend")).toHaveAttribute("data-position", "175,88");

    fireEvent.click(screen.getByRole("button", { name: "Move first graph node" }));

    expect(screen.getByTestId("graph-node-lead_backend")).toHaveAttribute("data-position", "250,260");
  });

  it("renders an empty graph state gracefully", () => {
    const lead = withKnowledgeGraph({
      nodes: [],
      edges: [],
      sources: [],
      related_leads: [],
      warnings: []
    });

    render(<KnowledgeGraph lead={lead} />);

    expect(screen.getByText("No graph context available.")).toBeInTheDocument();
  });
});

function withKnowledgeGraph(
  knowledgeGraph: FixtureLead["knowledgeGraph"] = {
    nodes: [
      {
        id: "lead_backend",
        kind: "lead",
        label: "Backend Contact",
        subtitle: "Current inbound lead",
        source_fact_ids: []
      },
      {
        id: "company_backend",
        kind: "company",
        label: "Backend Company",
        subtitle: "Submitted company",
        source_fact_ids: []
      }
    ],
    edges: [
      {
        id: "edge_backend",
        source: "lead_backend",
        target: "company_backend",
        relationship: "WORKS_AT",
        reason: "Submitted company.",
        confidence: 0.9,
        source_fact_ids: []
      }
    ],
    sources: [],
    related_leads: [],
    warnings: []
  }
): FixtureLead {
  const lead = leads.find((item) => item.name === "Sarah Chen");
  expect(lead).toBeDefined();
  return {
    ...lead!,
    name: "Backend Contact",
    company: "Backend Company",
    knowledgeGraph
  };
}
