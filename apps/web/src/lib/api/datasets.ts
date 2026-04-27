import { apiFetch } from "@/lib/api/client";
import type {
  BenchmarkQueryDetailResponse,
  BenchmarkQueryListResponse,
  ChunkDetailResponse,
  ChunkListResponse,
  DatasetListResponse,
  DatasetStatsResponse,
  DocumentDetailResponse,
  DocumentListResponse,
  RelevanceJudgmentListResponse
} from "@/lib/api/types";

type ListParams = {
  datasetId?: string;
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

export function getDatasets(): Promise<DatasetListResponse> {
  return apiFetch<DatasetListResponse>("/api/v1/datasets");
}

export function getDatasetStats(datasetId: string): Promise<DatasetStatsResponse> {
  return apiFetch<DatasetStatsResponse>(`/api/v1/datasets/${encodeURIComponent(datasetId)}/stats`);
}

export function getDocuments(params: ListParams = {}): Promise<DocumentListResponse> {
  return apiFetch<DocumentListResponse>(
    `/api/v1/documents${queryString({
      dataset_id: params.datasetId,
      limit: params.limit ?? 25,
      offset: params.offset ?? 0
    })}`
  );
}

export function getDocument(documentId: string): Promise<DocumentDetailResponse> {
  return apiFetch<DocumentDetailResponse>(`/api/v1/documents/${encodeURIComponent(documentId)}`);
}

export function getChunks(
  params: ListParams & { documentId?: string; chunkingStrategy?: string } = {}
): Promise<ChunkListResponse> {
  return apiFetch<ChunkListResponse>(
    `/api/v1/chunks${queryString({
      dataset_id: params.datasetId,
      document_id: params.documentId,
      chunking_strategy: params.chunkingStrategy,
      limit: params.limit ?? 25,
      offset: params.offset ?? 0
    })}`
  );
}

export function getChunk(chunkId: string): Promise<ChunkDetailResponse> {
  return apiFetch<ChunkDetailResponse>(`/api/v1/chunks/${encodeURIComponent(chunkId)}`);
}

export function getBenchmarkQueries(
  params: ListParams & { split?: string } = {}
): Promise<BenchmarkQueryListResponse> {
  return apiFetch<BenchmarkQueryListResponse>(
    `/api/v1/benchmark-queries${queryString({
      dataset_id: params.datasetId,
      split: params.split,
      limit: params.limit ?? 25,
      offset: params.offset ?? 0
    })}`
  );
}

export function getBenchmarkQuery(queryId: string): Promise<BenchmarkQueryDetailResponse> {
  return apiFetch<BenchmarkQueryDetailResponse>(
    `/api/v1/benchmark-queries/${encodeURIComponent(queryId)}`
  );
}

export function getRelevanceJudgments(
  params: ListParams & {
    queryId?: string;
    documentId?: string;
    queryExternalId?: string;
    documentExternalId?: string;
  } = {}
): Promise<RelevanceJudgmentListResponse> {
  return apiFetch<RelevanceJudgmentListResponse>(
    `/api/v1/relevance-judgments${queryString({
      dataset_id: params.datasetId,
      query_id: params.queryId,
      document_id: params.documentId,
      query_external_id: params.queryExternalId?.trim(),
      document_external_id: params.documentExternalId?.trim(),
      limit: params.limit ?? 25,
      offset: params.offset ?? 0
    })}`
  );
}
