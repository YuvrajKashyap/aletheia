import { apiFetch } from "@/lib/api/client";
import { isSnapshotMode } from "@/lib/demo-mode";
import {
  getSnapshotApiHealth,
  getSnapshotDbHealth,
  getSnapshotModelStatus,
  getSnapshotOpenSearchHealth,
  getSnapshotQdrantHealth,
  getSnapshotQueueStatus,
  getSnapshotSystemEvents,
  getSnapshotWorkerHeartbeats
} from "@/lib/api/snapshot";
import type {
  DbHealthResponse,
  HealthResponse,
  ModelStatusResponse,
  OpenSearchHealthResponse,
  QdrantHealthResponse,
  QueueStatusResponse,
  SystemEventListResponse,
  WorkerHeartbeatListResponse
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

export function getApiHealth(): Promise<HealthResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotApiHealth());
  }

  return apiFetch<HealthResponse>("/api/v1/health");
}

export function getDbHealth(): Promise<DbHealthResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotDbHealth());
  }

  return apiFetch<DbHealthResponse>("/api/v1/health/db");
}

export function getOpenSearchHealth(): Promise<OpenSearchHealthResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotOpenSearchHealth());
  }

  return apiFetch<OpenSearchHealthResponse>("/api/v1/system/opensearch");
}

export function getQdrantHealth(): Promise<QdrantHealthResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotQdrantHealth());
  }

  return apiFetch<QdrantHealthResponse>("/api/v1/system/qdrant");
}

export function getQueueStatus(): Promise<QueueStatusResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotQueueStatus());
  }

  return apiFetch<QueueStatusResponse>("/api/v1/system/queue");
}

export function getWorkerHeartbeats(): Promise<WorkerHeartbeatListResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotWorkerHeartbeats());
  }

  return apiFetch<WorkerHeartbeatListResponse>("/api/v1/system/worker-heartbeats");
}

export function getEmbeddingModelStatus(): Promise<ModelStatusResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotModelStatus("BAAI/bge-small-en-v1.5"));
  }

  return apiFetch<ModelStatusResponse>("/api/v1/system/models/embedding");
}

export function getRerankerModelStatus(): Promise<ModelStatusResponse> {
  if (isSnapshotMode()) {
    return Promise.resolve(getSnapshotModelStatus("cross-encoder/ms-marco-MiniLM-L-6-v2"));
  }

  return apiFetch<ModelStatusResponse>("/api/v1/system/models/reranker");
}

export function getSystemEvents(params: {
  eventType?: string;
  severity?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<SystemEventListResponse> {
  if (isSnapshotMode()) {
    return getSnapshotSystemEvents(params);
  }

  return apiFetch<SystemEventListResponse>(
    `/api/v1/system/events${queryString({
      event_type: params.eventType,
      severity: params.severity && params.severity !== "all" ? params.severity : undefined,
      limit: params.limit ?? 50,
      offset: params.offset ?? 0
    })}`
  );
}
