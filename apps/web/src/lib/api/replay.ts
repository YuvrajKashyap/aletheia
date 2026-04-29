import { apiFetch } from "@/lib/api/client";
import { isSnapshotMode } from "@/lib/demo-mode";
import {
  getSnapshotQueryReplay,
  getSnapshotQueryReplays,
  getSnapshotSavedQueries,
  getSnapshotSavedQuery
} from "@/lib/api/snapshot";
import type {
  JobStatusResponse,
  QueryReplayDetail,
  QueryReplayListResponse,
  ReplayResponse,
  ReplaySavedQueryRequest,
  SavedQueryCreateRequest,
  SavedQueryDetail,
  SavedQueryItem,
  SavedQueryListResponse,
  SeedGoldenQueriesRequest,
  SeedGoldenQueriesResponse,
  StartGoldenReplayRequest
} from "@/lib/api/types";

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

function adminHeaders(adminApiKey: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Admin-API-Key": adminApiKey
  };
}

function snapshotDisabled(message: string): never {
  throw new Error(message);
}

export function getSavedQueries(params: {
  source?: string;
  datasetId?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<SavedQueryListResponse> {
  if (isSnapshotMode()) {
    return getSnapshotSavedQueries(params);
  }

  return apiFetch<SavedQueryListResponse>(
    `/api/v1/replay/saved-queries${queryString({
      source: params.source && params.source !== "all" ? params.source : undefined,
      dataset_id: params.datasetId,
      limit: params.limit ?? 50,
      offset: params.offset ?? 0
    })}`
  );
}

export function getSavedQuery(id: string): Promise<SavedQueryDetail> {
  if (isSnapshotMode()) {
    return getSnapshotSavedQuery(id);
  }

  return apiFetch<SavedQueryDetail>(`/api/v1/replay/saved-queries/${encodeURIComponent(id)}`);
}

export function createSavedQuery(
  request: SavedQueryCreateRequest,
  adminApiKey: string
): Promise<SavedQueryDetail | SavedQueryItem> {
  if (isSnapshotMode()) {
    snapshotDisabled("Creating saved queries is disabled in public snapshot mode.");
  }

  return apiFetch<SavedQueryDetail>("/api/v1/replay/saved-queries", {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function seedGoldenQueries(
  request: SeedGoldenQueriesRequest,
  adminApiKey: string
): Promise<SeedGoldenQueriesResponse> {
  if (isSnapshotMode()) {
    snapshotDisabled("Seeding golden queries is disabled in public snapshot mode.");
  }

  return apiFetch<SeedGoldenQueriesResponse>("/api/v1/replay/saved-queries/seed-golden", {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function runSavedQueryReplay(
  savedQueryId: string,
  request: ReplaySavedQueryRequest,
  adminApiKey: string
): Promise<ReplayResponse> {
  if (isSnapshotMode()) {
    snapshotDisabled("Running saved query replays is disabled in public snapshot mode.");
  }

  return apiFetch<ReplayResponse>(`/api/v1/replay/saved-queries/${encodeURIComponent(savedQueryId)}/run`, {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function runGoldenReplay(
  request: StartGoldenReplayRequest,
  adminApiKey: string
): Promise<ReplayResponse> {
  if (isSnapshotMode()) {
    snapshotDisabled("Running golden replay batches is disabled in public snapshot mode.");
  }

  return apiFetch<ReplayResponse>("/api/v1/replay/golden/run", {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function getQueryReplays(params: {
  savedQueryId?: string;
  status?: string | "all";
  limit?: number;
  offset?: number;
} = {}): Promise<QueryReplayListResponse> {
  if (isSnapshotMode()) {
    return getSnapshotQueryReplays(params);
  }

  return apiFetch<QueryReplayListResponse>(
    `/api/v1/replay/runs${queryString({
      saved_query_id: params.savedQueryId,
      status: params.status && params.status !== "all" ? params.status : undefined,
      limit: params.limit ?? 50,
      offset: params.offset ?? 0
    })}`
  );
}

export function getQueryReplay(id: string): Promise<QueryReplayDetail> {
  if (isSnapshotMode()) {
    return getSnapshotQueryReplay(id);
  }

  return apiFetch<QueryReplayDetail>(`/api/v1/replay/runs/${encodeURIComponent(id)}`);
}

export function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  if (isSnapshotMode()) {
    snapshotDisabled("Replay job status refresh is disabled in public snapshot mode.");
  }

  return apiFetch<JobStatusResponse>(`/api/v1/system/jobs/${encodeURIComponent(jobId)}`);
}
