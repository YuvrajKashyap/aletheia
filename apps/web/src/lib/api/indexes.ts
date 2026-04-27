import { apiFetch } from "@/lib/api/client";
import type {
  BuildIndexJobResponse,
  CreateIndexVersionRequest,
  IndexJobListResponse,
  IndexStatusResponse,
  IndexVersionItem,
  IndexVersionListResponse,
  JobStatusResponse,
  OpenSearchHealthResponse,
  QdrantHealthResponse
} from "@/lib/api/types";

type VersionParams = {
  datasetId?: string;
  status?: string | "all";
  limit?: number;
  offset?: number;
};

type JobParams = {
  indexVersionId?: string;
  jobType?: string;
  status?: string | "all";
  limit?: number;
  offset?: number;
};

function queryString(params: Record<string, string | number | boolean | undefined>): string {
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

export function getIndexStatus(): Promise<IndexStatusResponse> {
  return apiFetch<IndexStatusResponse>("/api/v1/indexes/status");
}

export function getIndexVersions(params: VersionParams = {}): Promise<IndexVersionListResponse> {
  return apiFetch<IndexVersionListResponse>(
    `/api/v1/indexes/versions${queryString({
      dataset_id: params.datasetId,
      status: params.status && params.status !== "all" ? params.status : undefined,
      limit: params.limit ?? 50,
      offset: params.offset ?? 0
    })}`
  );
}

export function getIndexVersion(id: string): Promise<IndexVersionItem> {
  return apiFetch<IndexVersionItem>(`/api/v1/indexes/versions/${encodeURIComponent(id)}`);
}

export function getIndexJobs(params: JobParams = {}): Promise<IndexJobListResponse> {
  return apiFetch<IndexJobListResponse>(
    `/api/v1/indexes/jobs${queryString({
      index_version_id: params.indexVersionId,
      job_type: params.jobType,
      status: params.status && params.status !== "all" ? params.status : undefined,
      limit: params.limit ?? 50,
      offset: params.offset ?? 0
    })}`
  );
}

export function createIndexVersion(
  request: CreateIndexVersionRequest,
  adminApiKey: string
): Promise<IndexVersionItem> {
  return apiFetch<IndexVersionItem>("/api/v1/indexes/versions", {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function markIndexVersionReady(id: string, adminApiKey: string): Promise<IndexVersionItem> {
  return apiFetch<IndexVersionItem>(`/api/v1/indexes/versions/${encodeURIComponent(id)}/mark-ready`, {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify({})
  });
}

export function activateIndexVersion(id: string, adminApiKey: string): Promise<unknown> {
  return apiFetch<unknown>(`/api/v1/indexes/versions/${encodeURIComponent(id)}/activate`, {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify({})
  });
}

export function rollbackIndexVersion(id: string, adminApiKey: string): Promise<unknown> {
  return apiFetch<unknown>(`/api/v1/indexes/versions/${encodeURIComponent(id)}/rollback`, {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify({})
  });
}

export function buildLexicalIndex(
  id: string,
  request: { recreate?: boolean; limit?: number | null; refresh?: boolean },
  adminApiKey: string
): Promise<BuildIndexJobResponse> {
  return apiFetch<BuildIndexJobResponse>(`/api/v1/indexes/versions/${encodeURIComponent(id)}/build-lexical`, {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function buildVectorIndex(
  id: string,
  request: { recreate?: boolean; limit?: number | null; batch_size?: number | null },
  adminApiKey: string
): Promise<BuildIndexJobResponse> {
  return apiFetch<BuildIndexJobResponse>(`/api/v1/indexes/versions/${encodeURIComponent(id)}/build-vector`, {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return apiFetch<JobStatusResponse>(`/api/v1/system/jobs/${encodeURIComponent(jobId)}`);
}

export function getOpenSearchHealth(): Promise<OpenSearchHealthResponse> {
  return apiFetch<OpenSearchHealthResponse>("/api/v1/system/opensearch");
}

export function getQdrantHealth(): Promise<QdrantHealthResponse> {
  return apiFetch<QdrantHealthResponse>("/api/v1/system/qdrant");
}
