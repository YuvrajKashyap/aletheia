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
  id?: string;
  name?: string;
  status?: string;
  recall_at_10?: number | null;
  mrr_at_10?: number | null;
  ndcg_at_10?: number | null;
  config_json?: {
    retrieval_mode?: string;
    experiment_config_name?: string;
  };
  report_path?: string | null;
  created_at?: string;
};

export type EvaluationRunListResponse = {
  total?: number;
  limit?: number;
  offset?: number;
  items?: EvaluationRunItem[];
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

export type TraceListItem = {
  trace_id?: string;
  query_id?: string;
  query_text?: string;
  retrieval_mode?: string;
  status?: string;
  total_latency_ms?: number | null;
  result_count?: number | null;
  created_at?: string;
};

export type TraceListResponse = {
  total?: number;
  limit?: number;
  offset?: number;
  items?: TraceListItem[];
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

export type SearchMode = "bm25" | "dense" | "hybrid" | "hybrid_rerank";

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
