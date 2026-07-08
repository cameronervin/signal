const API_BASE_URL = process.env.NEXT_PUBLIC_SIGNAL_API_BASE_URL ?? "http://127.0.0.1:8000";
const FIXTURE_MODE =
  process.env.NEXT_PUBLIC_SIGNAL_USE_FIXTURES === "true" || process.env.SIGNAL_USE_FIXTURES === "true";

export function isFixtureMode() {
  return FIXTURE_MODE;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
    cache: "no-store"
  });

  if (!response.ok) {
    throw await apiError(response);
  }

  return response.json() as Promise<T>;
}

export async function apiPost<T, TBody = unknown>(path: string, body?: TBody): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      ...(body === undefined ? {} : { "Content-Type": "application/json" })
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    cache: "no-store"
  });

  if (!response.ok) {
    throw await apiError(response);
  }

  return response.json() as Promise<T>;
}

async function apiError(response: Response) {
  let detail: string | undefined;
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      detail = body.detail;
    }
  } catch {
    detail = undefined;
  }

  return new Error(`API request failed: ${response.status}${detail ? `: ${detail}` : ""}`);
}
