export type HealthResponse = {
  status?: string;
  service?: string;
  version?: string;
  app_mode?: string;
  request_id?: string;
};

export type DbHealthResponse = {
  status?: string;
  database?: string;
  request_id?: string;
  error?: string | null;
};

export type OpenSearchHealthResponse = {
  status?: string;
  url?: string;
  cluster_name?: string | null;
  version?: string | null;
  error?: string | null;
};

export type QdrantHealthResponse = {
  status?: string;
  url?: string;
  version?: string | null;
  collections_count?: number | null;
  error?: string | null;
};

export type IndexVersionItem = {
  id?: string;
  name?: string;
  status?: string;
  is_active?: boolean;
  lexical_index_name?: string | null;
  vector_collection_name?: string | null;
  embedding_model?: string | null;
  embedding_dimension?: number | null;
  chunk_count?: number | null;
  vector_count?: number | null;
  document_count?: number | null;
};

export type IndexStatusResponse = {
  active_index_version?: IndexVersionItem | null;
  dataset_count?: number;
  index_version_count?: number;
  ready_index_version_count?: number;
  active_index_version_count?: number;
  latest_index_versions?: IndexVersionItem[];
};

export type EvaluationRunItem = {
  id: string;
  name: string;
  dataset_id?: string | null;
  index_version_id?: string | null;
  experiment_config_id?: string | null;
  retrieval_mode?: string | null;
  status: string;
  query_count: number;
  failed_query_count: number;
  recall_at_5?: number | null;
  recall_at_10?: number | null;
  mrr_at_10?: number | null;
  ndcg_at_10?: number | null;
  avg_latency_ms?: number | null;
  p50_latency_ms?: number | null;
  p95_latency_ms?: number | null;
  report_path?: string | null;
  created_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  config_json?: Record<string, unknown>;
};

export type EvaluationRunListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: EvaluationRunItem[];
};

export type EvaluationRunDetail = EvaluationRunItem & {
  config_json?: Record<string, unknown>;
  notes?: string | null;
};

export type EvaluationQueryResultItem = {
  id: string;
  evaluation_run_id: string;
  benchmark_query_id?: string | null;
  query_external_id: string;
  query_text: string;
  recall_at_5?: number | null;
  recall_at_10?: number | null;
  mrr_at_10?: number | null;
  ndcg_at_10?: number | null;
  latency_ms?: number | null;
  trace_id?: string | null;
  error_message?: string | null;
  created_at?: string | null;
};

export type EvaluationQueryResultListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: EvaluationQueryResultItem[];
};

export type EvaluationReportResponse = {
  evaluation_run_id: string;
  report_path?: string | null;
  report_format?: string | null;
  summary_json?: Record<string, unknown>;
  report_json?: Record<string, unknown> | null;
  warning?: string | null;
};

export type ExperimentConfigItem = {
  id?: string;
  name?: string;
  retrieval_mode?: string;
  is_default?: boolean;
  top_k_final?: number;
};

export type ExperimentConfigListResponse = {
  total?: number;
  limit?: number;
  offset?: number;
  items?: ExperimentConfigItem[];
};

export type SearchMode = "bm25" | "dense" | "hybrid" | "hybrid_rerank";

export type TraceListItem = {
  trace_id: string;
  query_id: string;
  query_text: string;
  retrieval_mode: SearchMode;
  status: string;
  total_latency_ms?: number | null;
  result_count?: number | null;
  created_at?: string | null;
};

export type TraceListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: TraceListItem[];
};

export type TraceCandidateItem = {
  id?: string;
  source: string;
  final_rank?: number | null;
  bm25_rank?: number | null;
  dense_rank?: number | null;
  fusion_rank?: number | null;
  rerank_rank?: number | null;
  bm25_score?: number | null;
  dense_score?: number | null;
  fusion_score?: number | null;
  reranker_score?: number | null;
  chunk_id?: string | null;
  document_id?: string | null;
  metadata_json?: Record<string, unknown>;
  created_at?: string | null;
};

export type TraceDetailResponse = {
  trace_id: string;
  query_id: string;
  query_text: string;
  retrieval_mode: SearchMode;
  index_version_id?: string | null;
  status: string;
  total_latency_ms?: number | null;
  trace_schema_version?: string | null;
  trace_json: Record<string, unknown>;
  ranking_summary?: Record<string, unknown>;
  candidates: TraceCandidateItem[];
  candidates_by_source?: Record<string, TraceCandidateItem[]>;
  created_at?: string | null;
};

export type TraceCandidateListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: TraceCandidateItem[];
};

export type DatasetItem = {
  id?: string;
  name?: string;
  version?: string;
  source?: string | null;
  document_count?: number;
  benchmark_query_count?: number;
  relevance_judgment_count?: number;
  created_at?: string;
};

export type DatasetListResponse = DatasetItem[];

export type SavedQueryItem = {
  id?: string;
  name?: string | null;
  text?: string;
  source?: string;
  metadata_json?: {
    query_external_id?: string;
    relevance_count?: number;
  };
  created_at?: string;
};

export type SavedQueryListResponse = {
  total?: number;
  limit?: number;
  offset?: number;
  items?: SavedQueryItem[];
};

export type SearchRequest = {
  query: string;
  retrieval_mode: SearchMode;
  top_k: number;
  candidate_k?: number | null;
  bm25_candidate_k?: number | null;
  dense_candidate_k?: number | null;
  hybrid_candidate_k?: number | null;
  rerank_top_n?: number | null;
  rrf_k?: number | null;
  index_version_id?: string | null;
};

export type SearchResultItem = {
  rank: number;
  chunk_id: string;
  document_id?: string | null;
  dataset_id?: string | null;
  document_external_id?: string | null;
  chunk_external_id?: string | null;
  title?: string | null;
  text: string;
  score?: number | null;
  score_breakdown?: Record<string, number | string | null>;
  token_count?: number | null;
  chunking_strategy?: string | null;
  chunking_version?: string | null;
  metadata_json?: Record<string, unknown>;
};

export type SearchResponse = {
  query_id: string;
  trace_id: string;
  request_id?: string | null;
  query: string;
  retrieval_mode: SearchMode;
  index_version_id?: string | null;
  index_name?: string | null;
  lexical_index_name?: string | null;
  collection_name?: string | null;
  vector_collection_name?: string | null;
  top_k: number;
  candidate_k?: number | null;
  bm25_candidate_k?: number | null;
  dense_candidate_k?: number | null;
  hybrid_candidate_k?: number | null;
  rerank_top_n?: number | null;
  rrf_k?: number | null;
  latency_ms?: number | null;
  bm25_latency_ms?: number | null;
  dense_latency_ms?: number | null;
  embedding_latency_ms?: number | null;
  qdrant_latency_ms?: number | null;
  fusion_latency_ms?: number | null;
  reranker_latency_ms?: number | null;
  result_count: number;
  results: SearchResultItem[];
};
