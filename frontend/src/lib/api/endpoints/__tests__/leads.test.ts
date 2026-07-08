import { apiGet, isFixtureMode } from "@/lib/api/client";
import { getLead } from "@/lib/api/endpoints/leads";
import type { LeadResponseDto } from "@/types/lead";

jest.mock("@/lib/api/client", () => ({
  apiGet: jest.fn(),
  isFixtureMode: jest.fn()
}));

const apiGetMock = jest.mocked(apiGet);
const isFixtureModeMock = jest.mocked(isFixtureMode);

describe("lead API endpoint mapping", () => {
  beforeEach(() => {
    apiGetMock.mockReset();
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
