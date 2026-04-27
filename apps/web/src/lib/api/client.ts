import { API_BASE_URL } from "@/lib/config";

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, message: string, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function readResponseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

function errorMessage(status: number, body: unknown): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    return JSON.stringify(detail);
  }
  if (typeof body === "string" && body.trim()) {
    return body;
  }
  return `API request failed with status ${status}`;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (!path.startsWith("/api/v1/")) {
    throw new Error("apiFetch path must start with /api/v1/");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: "application/json",
      ...options.headers
    },
    cache: options.cache ?? "no-store"
  });

  if (!response.ok) {
    const body = await readResponseBody(response);
    throw new ApiError(response.status, errorMessage(response.status, body), body);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await readResponseBody(response)) as T;
}
