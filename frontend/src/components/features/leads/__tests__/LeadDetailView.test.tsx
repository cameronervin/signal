import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";

import { KnowledgeGraph } from "@/components/features/leads/KnowledgeGraph";
import { LeadDetailView } from "@/components/features/leads/LeadDetailView";
import { leads } from "@/lib/fixtures/leads";
import type { FixtureLead } from "@/types/lead";

jest.mock("@xyflow/react", () => ({
  Background: () => null,
  ReactFlow: ({
    children,
    nodes = [],
    edges = []
  }: {
    children: ReactNode;
    nodes?: Array<{ id: string; data?: { label?: string } }>;
    edges?: Array<{ id: string; label?: string }>;
  }) => (
    <div data-testid="knowledge-graph">
      {nodes.map((node) => (
        <span key={node.id} data-testid={`graph-node-${node.id}`}>
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
  )
}));

describe("LeadDetailView", () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined)
      }
    });
  });

  it("renders an editable draft and no live send action for workable leads", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(screen.getByDisplayValue("Improving leasing response in Austin")).toBeInTheDocument();
    expect(screen.getByText("Review gate")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^send$/i })).not.toBeInTheDocument();

    fireEvent.change(screen.getByDisplayValue("Improving leasing response in Austin"), {
      target: { value: "Updated subject" }
    });
    expect(screen.getByDisplayValue("Updated subject")).toBeInTheDocument();
  });

  it("keeps drafted email sources closed by default", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    const sourcesDisclosure = screen.getByText("Sources").closest("details");
    expect(sourcesDisclosure).toBeInTheDocument();
    expect(sourcesDisclosure).not.toHaveAttribute("open");
  });

  it("hides seeded related-history text from the knowledge graph notes", () => {
    const lead = leads.find((item) => item.name === "Sarah Chen");
    expect(lead).toBeDefined();

    render(<LeadDetailView lead={lead!} />);

    expect(screen.queryByText("Related inbound")).not.toBeInTheDocument();
    expect(screen.queryByText("Same company appeared in fixture history")).not.toBeInTheDocument();
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
