import { apiGet, apiPost, isFixtureMode } from "@/lib/api/client";
import { createLead, getLead } from "@/lib/api/endpoints/leads";
import type { AgentRunResponseDto, LeadCreateDto, LeadResponseDto } from "@/types/lead";

jest.mock("@/lib/api/client", () => ({
  apiGet: jest.fn(),
  apiPost: jest.fn(),
  isFixtureMode: jest.fn()
}));

const apiGetMock = jest.mocked(apiGet);
const apiPostMock = jest.mocked(apiPost);
const isFixtureModeMock = jest.mocked(isFixtureMode);

describe("lead API endpoint mapping", () => {
  beforeEach(() => {
    apiGetMock.mockReset();
    apiPostMock.mockReset();
    isFixtureModeMock.mockReturnValue(false);
  });

  it("defaults omitted backend array fields before rendering lead detail", async () => {
    apiGetMock.mockResolvedValueOnce(backendLeadWithoutArrayFields());

    const lead = await getLead("11111111-1111-4111-8111-111111111111");

    expect(apiGetMock).toHaveBeenCalledWith("/api/v1/leads/11111111-1111-4111-8111-111111111111");
    expect(lead?.talkingPoints).toEqual([]);
    expect(lead?.flags).toEqual([]);
    expect(lead?.related).toEqual([]);
    expect(lead?.gates.failures).toEqual([]);
    expect(lead?.draft?.sources).toEqual([]);
  });

  it("deduplicates repeated backend sales insights", async () => {
    apiGetMock.mockResolvedValueOnce({
      ...backendLeadWithoutArrayFields(),
      talking_points: [
        "Related lead context: Shared source category.",
        "Related lead context: Shared source category."
      ]
    });

    const lead = await getLead("11111111-1111-4111-8111-111111111111");

    expect(lead?.talkingPoints).toEqual([
      "Related lead context: Shared source category."
    ]);
  });

  it("preserves related lead ids as hidden frontend identity", async () => {
    apiGetMock.mockResolvedValueOnce({
      ...backendLeadWithoutArrayFields(),
      related_leads: [
        {
          lead_id: "11111111-2222-4222-8222-111111111111",
          label: "Related inbound",
          reason: "Shared source category."
        },
        {
          lead_id: "11111111-3333-4333-8333-111111111111",
          label: "Related inbound",
          reason: "Shared source category."
        }
      ]
    });

    const lead = await getLead("11111111-1111-4111-8111-111111111111");

    expect(lead?.related).toEqual([
      {
        id: "11111111-2222-4222-8222-111111111111",
        label: "Related inbound",
        reason: "Shared source category."
      },
      {
        id: "11111111-3333-4333-8333-111111111111",
        label: "Related inbound",
        reason: "Shared source category."
      }
    ]);
  });

  it("posts lead submissions with the backend create contract", async () => {
    const payload: LeadCreateDto = {
      contact_name: "Sample Contact",
      email: "contact@operator.example",
      company: "Multifamily Operator",
      role: null,
      property_address: "100 Main St",
      city: "Austin",
      state: "TX",
      country: "US"
    };
    const response: AgentRunResponseDto = {
      run_id: "21111111-1111-4111-8111-111111111111",
      lead_id: "11111111-1111-4111-8111-111111111111",
      status: "queued",
      trigger: "api_insert",
      current_stage: "queued",
      steps: [],
      activity_log: ["api_insert: lead received", "agent_run: queued"]
    };
    apiPostMock.mockResolvedValueOnce(response);

    await expect(createLead(payload)).resolves.toEqual(response);

    expect(apiPostMock).toHaveBeenCalledWith("/api/v1/leads", payload);
  });
});

function backendLeadWithoutArrayFields(): LeadResponseDto {
  return {
    id: "11111111-1111-4111-8111-111111111111",
    input: {
      contact_name: "Sample Contact",
      email: "lead@sampleoperator.example",
      company: "Sample Multifamily Group",
      role: "VP Leasing",
      property_address: "100 Main St",
      city: "Austin",
      state: "TX",
      country: "US"
    },
    gates: {
      status: "passed"
    },
    enrichment: {
      market: "Austin, TX",
      coordinates: null,
      renter_share: null,
      median_rent: null,
      rent_growth_yoy: null,
      household_growth: null,
      unemployment_rate: null,
      company_units: null,
      recent_trigger: null,
      sources: []
    },
    score: {
      total: 82,
      tier: "A",
      company_fit: 40,
      market_opportunity: 32,
      bonuses: 10,
      why_line: "senior contact",
      components: {}
    },
    draft: {
      subject: "Review leasing response",
      body: "Sample draft"
    },
    run_id: "21111111-1111-4111-8111-111111111111"
  } as unknown as LeadResponseDto;
}
