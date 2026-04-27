import { apiFetch } from "@/lib/api/client";
import type {
  DatasetListResponse,
  DbHealthResponse,
  EvaluationRunListResponse,
  ExperimentConfigListResponse,
  HealthResponse,
  IndexStatusResponse,
  OpenSearchHealthResponse,
  QdrantHealthResponse,
  SavedQueryListResponse,
  TraceListResponse
} from "@/lib/api/types";

export function getHealth() {
  return apiFetch<HealthResponse>("/api/v1/health");
}

export function getDbHealth() {
  return apiFetch<DbHealthResponse>("/api/v1/health/db");
}

export function getOpenSearchHealth() {
  return apiFetch<OpenSearchHealthResponse>("/api/v1/system/opensearch");
}

export function getQdrantHealth() {
  return apiFetch<QdrantHealthResponse>("/api/v1/system/qdrant");
}

export function getIndexStatus() {
  return apiFetch<IndexStatusResponse>("/api/v1/indexes/status");
}

export function getLatestEvaluationRuns(limit = 5) {
  return apiFetch<EvaluationRunListResponse>(`/api/v1/evaluations/runs?limit=${limit}&offset=0`);
}

export function getExperimentConfigs(limit = 8) {
  return apiFetch<ExperimentConfigListResponse>(`/api/v1/experiments/configs?limit=${limit}&offset=0`);
}

export function getRecentTraces(limit = 5) {
  return apiFetch<TraceListResponse>(`/api/v1/search/traces?limit=${limit}&offset=0`);
}

export function getDatasets() {
  return apiFetch<DatasetListResponse>("/api/v1/datasets");
}

export function getSavedQueries(limit = 5) {
  return apiFetch<SavedQueryListResponse>(`/api/v1/replay/saved-queries?limit=${limit}&offset=0`);
}
