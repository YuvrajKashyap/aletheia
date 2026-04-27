import { apiFetch } from "@/lib/api/client";
import type {
  SearchMode,
  TraceCandidateListResponse,
  TraceDetailResponse,
  TraceListResponse
} from "@/lib/api/types";

type TraceListParams = {
  retrievalMode?: SearchMode | "all";
  status?: string | "all";
  limit?: number;
  offset?: number;
};

type TraceCandidateParams = {
  source?: string;
  limit?: number;
  offset?: number;
};

function queryString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

export function getTraces(params: TraceListParams = {}): Promise<TraceListResponse> {
  return apiFetch<TraceListResponse>(
    `/api/v1/search/traces${queryString({
      retrieval_mode: params.retrievalMode && params.retrievalMode !== "all" ? params.retrievalMode : undefined,
      status: params.status && params.status !== "all" ? params.status : undefined,
      limit: params.limit ?? 25,
      offset: params.offset ?? 0
    })}`
  );
}

export function getTrace(traceId: string): Promise<TraceDetailResponse> {
  return apiFetch<TraceDetailResponse>(`/api/v1/search/traces/${encodeURIComponent(traceId)}`);
}

export function getTraceCandidates(
  traceId: string,
  params: TraceCandidateParams = {}
): Promise<TraceCandidateListResponse> {
  return apiFetch<TraceCandidateListResponse>(
    `/api/v1/search/traces/${encodeURIComponent(traceId)}/candidates${queryString({
      source: params.source,
      limit: params.limit ?? 100,
      offset: params.offset ?? 0
    })}`
  );
}
