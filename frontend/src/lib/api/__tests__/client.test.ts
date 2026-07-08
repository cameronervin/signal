import { apiPost } from "@/lib/api/client";

describe("apiPost", () => {
  const fetchMock = jest.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    fetchMock.mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({ status: "ok" })
    });
    global.fetch = fetchMock;
  });

  it("preserves no-body POST requests", async () => {
    await apiPost("/api/v1/agent-runs/run-1/pause");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/agent-runs/run-1/pause",
      expect.objectContaining({
        method: "POST",
        headers: { Accept: "application/json" },
        cache: "no-store"
      })
    );
    expect(fetchMock.mock.calls[0][1]).not.toHaveProperty("body");
  });

  it("sends JSON when a body is provided", async () => {
    const body = { contact_name: "Sample Contact" };

    await apiPost("/api/v1/leads", body);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/leads",
      expect.objectContaining({
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify(body),
        cache: "no-store"
      })
    );
  });
});
