import type { FixtureAgentRun, FixtureLead } from "@/types/lead";

export const leads: FixtureLead[] = [
  {
    id: "lead-sarah-chen",
    name: "Sarah Chen",
    email: "sarah@meridianresidential.example",
    role: "VP Leasing",
    company: "Meridian Residential",
    market: "Austin, TX",
    units: 85000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 92,
      tier: "A",
      whyLine: "Large portfolio · senior contact · 8.1% rent growth · recent trigger event"
    },
    flags: [],
    talkingPoints: [
      "Austin renter share is 61%, which can create concentrated leasing demand.",
      "Local rent growth is 8.1% year over year.",
      "Portfolio scale suggests centralized leasing operations and measurable queue pressure."
    ],
    marketSignals: [
      { label: "Renter", value: "61%" },
      { label: "Rent YoY", value: "+8.1%" },
      { label: "Unemployment", value: "3.2%" },
      { label: "HH growth", value: "+4.4%" }
    ],
    related: [{ label: "Related inbound", reason: "Same company appeared in fixture history" }],
    draft: {
      subject: "Improving leasing response in Austin",
      body:
        "Hi Sarah,\n\nI noticed Meridian Residential announced regional portfolio expansion. Public market data also points to 61% renter share and 8.1% rent growth in Austin.\n\nSignal flagged this as a strong fit because leasing teams can use faster response, cleaner prioritization, and better follow-up visibility when inbound demand spikes.\n\nWould it be worth comparing how your team is handling those leads today?",
      sources: [
        { source: "Census ACS", label: "Renter share", value: "61%" },
        { source: "FRED", label: "Rent growth", value: "8.1% YoY" },
        { source: "News", label: "Trigger", value: "Regional portfolio expansion" }
      ]
    }
  },
  {
    id: "lead-marcus-webb",
    name: "Marcus Webb",
    email: "marcus@northstarliving.example",
    role: "Director Operations",
    company: "Northstar Living",
    market: "Charlotte, NC",
    units: 85000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 84,
      tier: "A",
      whyLine: "Large portfolio · senior contact · tight labor market"
    },
    flags: [],
    talkingPoints: [
      "Charlotte shows strong renter density for leasing demand.",
      "Director-level operations contact maps to workflow ownership.",
      "Labor market tightness can increase need for automation support."
    ],
    marketSignals: [
      { label: "Renter", value: "61%" },
      { label: "Rent YoY", value: "+8.1%" },
      { label: "Unemployment", value: "3.2%" },
      { label: "HH growth", value: "+4.4%" }
    ],
    related: [],
    draft: {
      subject: "Leasing response visibility in Charlotte",
      body:
        "Hi Marcus,\n\nSignal flagged Charlotte as a strong opportunity market based on renter density and labor conditions. For a portfolio at Northstar Living's scale, faster inbound triage can help reps focus on the leads most likely to convert.\n\nWould it be useful to compare your current speed-to-lead workflow against this market signal?",
      sources: [
        { source: "Census ACS", label: "Renter share", value: "61%" },
        { source: "FRED", label: "Labor market", value: "3.2% unemployment" }
      ]
    }
  },
  {
    id: "lead-robert-diaz",
    name: "Robert Diaz",
    email: "robert@urban-nest.example",
    role: "Regional Manager",
    company: "Urban Nest Communities",
    market: "Seattle, WA",
    units: 42000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 71,
      tier: "B",
      whyLine: "Solid portfolio · regional contact · no recent trigger"
    },
    flags: [],
    talkingPoints: [
      "Regional title suggests operational context but may need economic buyer mapping.",
      "Market signal is useful, but timing signal is weaker without recent news.",
      "Good candidate for review after A-tier leads."
    ],
    marketSignals: [
      { label: "Renter", value: "48%" },
      { label: "Rent YoY", value: "+3.4%" },
      { label: "Unemployment", value: "3.2%" },
      { label: "HH growth", value: "+4.4%" }
    ],
    related: [],
    draft: {
      subject: "Inbound leasing prioritization in Seattle",
      body:
        "Hi Robert,\n\nSignal flagged your Seattle lead as a solid fit based on portfolio scale and local renter demand. The main opportunity is helping leasing teams separate urgent inbound requests from lower-fit inquiries without adding manual research.\n\nWould a quick workflow comparison be useful?",
      sources: [
        { source: "Census ACS", label: "Renter share", value: "48%" },
        { source: "FRED", label: "Rent growth", value: "3.4% YoY" }
      ]
    }
  },
  {
    id: "lead-priya-nair",
    name: "Priya Nair",
    email: "priya@copperline-homes.example",
    role: "Regional Manager",
    company: "Copperline Homes",
    market: "Arlington, VA",
    units: 44000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 78,
      tier: "A",
      whyLine: "High-density submarket · repeat inbound · strong fit signals"
    },
    flags: [],
    talkingPoints: [
      "Repeat inbound suggests active evaluation rather than a one-off inquiry.",
      "High renter density supports strong leasing-team workload.",
      "Regional ownership role can route the conversation to the right workflow owner."
    ],
    marketSignals: [
      { label: "Renter", value: "56%" },
      { label: "Rent YoY", value: "+5.9%" },
      { label: "Unemployment", value: "3.6%" },
      { label: "HH growth", value: "+3.1%" }
    ],
    related: [{ label: "Fixture history", reason: "Same market appeared in recent inbound" }],
    draft: {
      subject: "Prioritizing repeat inbound in Arlington",
      body:
        "Hi Priya,\n\nSignal flagged Copperline Homes because Arlington combines high renter density with repeat inbound activity. Those two signals often make response speed and lead routing more important.\n\nWould it be useful to compare how your team decides which leasing inquiries get worked first?",
      sources: [
        { source: "Census ACS", label: "Renter share", value: "56%" },
        { source: "FRED", label: "Rent growth", value: "5.9% YoY" }
      ]
    }
  },
  {
    id: "lead-david-okafor",
    name: "David Okafor",
    email: "david@sunhaven-residential.example",
    role: "Asset Manager",
    company: "Sunhaven Residential",
    market: "Nashville, TN",
    units: 102000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 71,
      tier: "B",
      whyLine: "Large footprint · mid-seniority title · strong market growth"
    },
    flags: [],
    talkingPoints: [
      "Portfolio scale points to enough inbound volume for prioritization to matter.",
      "Market growth is strong, but seniority signal is moderate.",
      "Best worked after the A-tier queue is stable."
    ],
    marketSignals: [
      { label: "Renter", value: "49%" },
      { label: "Rent YoY", value: "+6.2%" },
      { label: "Unemployment", value: "3.4%" },
      { label: "HH growth", value: "+3.8%" }
    ],
    related: [],
    draft: {
      subject: "Leasing triage for Nashville demand",
      body:
        "Hi David,\n\nSignal flagged Sunhaven Residential as a solid fit because Nashville demand is strong and your portfolio has enough scale for lead triage to create leverage.\n\nWould a short comparison of current inbound routing be useful?",
      sources: [
        { source: "Census ACS", label: "Renter share", value: "49%" },
        { source: "FRED", label: "Rent growth", value: "6.2% YoY" }
      ]
    }
  },
  {
    id: "lead-lin-zhao",
    name: "Lin Zhao",
    email: "lin@havenbridge-living.example",
    role: "Director Leasing",
    company: "Havenbridge Living",
    market: "Phoenix, AZ",
    units: 180000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 69,
      tier: "B",
      whyLine: "Large footprint · flat rent trend · no recent trigger"
    },
    flags: [],
    talkingPoints: [
      "Large footprint increases potential impact from cleaner inbound prioritization.",
      "Flat rent trend lowers urgency compared with top A-tier markets.",
      "A director-level leasing title is still a strong workflow signal."
    ],
    marketSignals: [
      { label: "Renter", value: "45%" },
      { label: "Rent YoY", value: "+1.1%" },
      { label: "Unemployment", value: "3.9%" },
      { label: "HH growth", value: "+2.9%" }
    ],
    related: [],
    draft: {
      subject: "A faster way to sort Phoenix leasing inquiries",
      body:
        "Hi Lin,\n\nSignal marked Havenbridge Living as a good fit because the portfolio scale makes prioritization valuable, even in a flatter rent-growth market.\n\nWould it be useful to see how top-fit inbound leads are separated from lower-fit inquiries?",
      sources: [
        { source: "Census ACS", label: "Renter share", value: "45%" },
        { source: "FRED", label: "Rent growth", value: "1.1% YoY" }
      ]
    }
  },
  {
    id: "lead-demo-pending",
    name: "Demo Contact B",
    email: "demo-contact-b@regional-operator-b.example",
    role: "Leasing Operations Manager",
    company: "Regional Operator B",
    market: "Raleigh, NC",
    units: 72000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 73,
      tier: "B",
      whyLine: "Good portfolio fit · draft pending source verification"
    },
    flags: [],
    talkingPoints: [
      "Portfolio scale supports prioritization value.",
      "Local demand signals are useful, but the draft is waiting on source verification.",
      "Best reviewed after the cited source set is complete."
    ],
    marketSignals: [
      { label: "Renter", value: "47%" },
      { label: "Rent YoY", value: "+3.6%" },
      { label: "Unemployment", value: "3.4%" },
      { label: "HH growth", value: "+3.2%" }
    ],
    related: [],
    draft: null
  },
  {
    id: "lead-jenna-cole",
    name: "Jenna Cole",
    email: "jenna@ridgeview-communities.example",
    role: "Property Manager",
    company: "Ridgeview Communities",
    market: "Denver, CO",
    units: 58000,
    gates: { status: "passed", failures: [] },
    score: {
      total: 64,
      tier: "B",
      whyLine: "Site-level title · single-market fit · good renter density"
    },
    flags: [],
    talkingPoints: [
      "Good renter density supports leasing need, but the title may be site-level.",
      "Work after stronger portfolio-level contacts.",
      "Useful candidate for manual verification or a routed follow-up."
    ],
    marketSignals: [
      { label: "Renter", value: "52%" },
      { label: "Rent YoY", value: "+2.8%" },
      { label: "Unemployment", value: "3.7%" },
      { label: "HH growth", value: "+2.5%" }
    ],
    related: [],
    draft: {
      subject: "Sorting inbound leasing requests in Denver",
      body:
        "Hi Jenna,\n\nSignal flagged Ridgeview Communities because Denver renter density still points to meaningful leasing demand. The opportunity may be in routing the right inquiries to the right team member faster.\n\nWould a short workflow comparison be useful?",
      sources: [
        { source: "Census ACS", label: "Renter share", value: "52%" },
        { source: "FRED", label: "Rent growth", value: "2.8% YoY" }
      ]
    }
  },
  {
    id: "lead-tom-whitaker",
    name: "Tom Whitaker",
    email: "tom@personalmail.example",
    role: "Property Manager",
    company: "Unverified Homes",
    market: "Miami, FL",
    units: null,
    gates: { status: "failed", failures: ["personal email domain", "company did not resolve"] },
    score: {
      total: 28,
      tier: "C",
      whyLine: "Gate failed: personal email domain, company did not resolve"
    },
    flags: ["personal email domain", "company did not resolve", "portfolio unverifiable"],
    talkingPoints: [],
    marketSignals: [],
    related: [],
    draft: null
  }
];

export const agentRuns: FixtureAgentRun[] = [
  {
    runId: "run-8842",
    agent: "Outreach Agent",
    kind: "Draft review",
    leadId: "lead-sarah-chen",
    lead: "Sarah Chen · Meridian Residential",
    started: "2m",
    stage: "Human review",
    stageIndex: 3,
    status: "awaiting_review",
    statusLabel: "Awaiting you",
    steps: [
      { name: "Deterministic enrichment", status: "done", summary: "Public data and domain checks completed." },
      {
        name: "Agent scoring and drafting",
        status: "done",
        summary: "Score 92, A-tier, draft generated with cited sources."
      },
      { name: "Knowledge graph", status: "done", summary: "Related company context attached." },
      { name: "Human review", status: "pending", summary: "Awaiting SDR review before copy or export." },
      { name: "Export", status: "pending", summary: "Runs only after human review." }
    ],
    activityLog: [
      "11:42:01 api_insert received",
      "11:42:02 deterministic enrichment completed",
      "11:42:05 scoring completed: 92 A",
      "11:42:08 draft generated with 3 cited facts",
      "11:42:09 knowledge graph linked 1 related lead",
      "11:42:11 awaiting human review"
    ]
  },
  {
    runId: "run-9011",
    agent: "Enrichment Agent",
    kind: "Lead enrichment",
    leadId: "lead-marcus-webb",
    lead: "Marcus Webb · Northstar Living",
    started: "9m",
    stage: "Scoring",
    stageIndex: 2,
    status: "running",
    statusLabel: "In progress",
    steps: [
      { name: "Deterministic enrichment", status: "done", summary: "Public data resolved." },
      { name: "Agent scoring and drafting", status: "running", summary: "Building score and draft." },
      { name: "Knowledge graph", status: "pending", summary: "Waiting on score output." },
      { name: "Human review", status: "pending", summary: "Not ready." }
    ],
    activityLog: ["11:35:02 api_insert received", "11:35:04 deterministic enrichment completed"]
  },
  {
    runId: "run-7750",
    agent: "Outreach Agent",
    kind: "Draft review",
    leadId: "lead-david-okafor",
    lead: "David Okafor · Sunhaven Residential",
    started: "1h",
    stage: "Exported",
    stageIndex: 4,
    status: "completed",
    statusLabel: "Exported",
    steps: [
      { name: "Deterministic enrichment", status: "done", summary: "Public data resolved." },
      { name: "Agent scoring and drafting", status: "done", summary: "Score 71, B-tier, draft generated." },
      { name: "Knowledge graph", status: "done", summary: "Related context attached." },
      { name: "Human review", status: "done", summary: "Approved by SDR." },
      { name: "Export", status: "done", summary: "Draft copied or exported for use in existing sales tools." }
    ],
    activityLog: ["10:18:01 api_insert received", "10:18:08 review approved", "10:18:12 draft exported"]
  },
  {
    runId: "run-next-release",
    agent: "Follow-up Agent",
    kind: "Next release",
    lead: "Auto-cadence outreach",
    started: "-",
    stage: "Human approval policy",
    stageIndex: 0,
    status: "queued",
    statusLabel: "Next release",
    disabled: true,
    steps: [],
    activityLog: []
  }
];

export function getLead(id: string): FixtureLead | undefined {
  return leads.find((lead) => lead.id === id);
}

export function getAgentRun(runId: string): FixtureAgentRun | undefined {
  return agentRuns.find((run) => run.runId === runId);
}
