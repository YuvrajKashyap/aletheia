import type {
  BenchmarkQueryDetailResponse,
  BenchmarkQueryListResponse,
  ChunkDetailResponse,
  ChunkListResponse,
  DatasetListResponse,
  DatasetStatsResponse,
  DocumentDetailResponse,
  DocumentListResponse,
  EvaluationQueryResultListResponse,
  EvaluationReportResponse,
  EvaluationRunDetail,
  EvaluationRunListResponse,
  ExperimentConfigListResponse,
  IndexJobListResponse,
  IndexStatusResponse,
  IndexVersionItem,
  IndexVersionListResponse,
  OpenSearchHealthResponse,
  QdrantHealthResponse,
  QueryReplayDetail,
  QueryReplayListResponse,
  RelevanceJudgmentListResponse,
  SavedQueryDetail,
  SavedQueryListResponse,
  SearchMode,
  SearchRequest,
  SearchResponse,
  SystemEventListResponse,
  TraceCandidateItem,
  TraceCandidateListResponse,
  TraceDetailResponse,
  TraceListResponse
} from "@/lib/api/types";

type SnapshotFileName =
  | "manifest.json"
  | "overview.json"
  | "index-status.json"
  | "datasets.json"
  | "documents-sample.json"
  | "chunks-sample.json"
  | "benchmark-queries-sample.json"
  | "relevance-judgments-sample.json"
  | "search-scenarios.json"
  | "traces.json"
  | "evaluations.json"
  | "experiments.json"
  | "replay.json"
  | "system.json";

type JsonRecord = Record<string, unknown>;

type PageParams = {
  limit?: number;
  offset?: number;
};

function snapshotUrl(fileName: string): string {
  const path = `/demo-data/${fileName}`;
  if (typeof window !== "undefined") {
    return path;
  }

  const configured = process.env.NEXT_PUBLIC_SITE_URL;
  if (configured) {
    return `${configured.replace(/\/+$/, "")}${path}`;
  }

  const vercelUrl = process.env.VERCEL_URL;
  if (vercelUrl) {
    return `https://${vercelUrl.replace(/\/+$/, "")}${path}`;
  }

  return `http://localhost:3000${path}`;
}

export async function fetchSnapshotFile<T>(fileName: SnapshotFileName): Promise<T> {
  const response = await fetch(snapshotUrl(fileName), {
    cache: "no-store",
    headers: {
      Accept: "application/json"
    }
  });

  if (!response.ok) {
    throw new Error(`Snapshot file ${fileName} is unavailable with status ${response.status}`);
  }

  return (await response.json()) as T;
}

function record(value: unknown): JsonRecord {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as JsonRecord) : {};
}

function array<T = JsonRecord>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value : undefined;
}

function page<T>(items: T[], params: PageParams = {}) {
  const limit = params.limit ?? 25;
  const offset = params.offset ?? 0;
  return {
    total: items.length,
    limit,
    offset,
    items: items.slice(offset, offset + limit)
  };
}

function snapshotDisabled(message: string): never {
  throw new Error(message);
}

export function getSnapshotManifest() {
  return fetchSnapshotFile<JsonRecord>("manifest.json");
}

export function getSnapshotOverview() {
  return fetchSnapshotFile<JsonRecord>("overview.json");
}

export async function getSnapshotSearchScenarios() {
  return fetchSnapshotFile<{ items?: SearchResponse[] | JsonRecord[]; warnings?: string[] }>("search-scenarios.json");
}

export async function runSnapshotSearch(request: SearchRequest): Promise<SearchResponse> {
  const scenarios = await getSnapshotSearchScenarios();
  const items = array<JsonRecord>(scenarios.items);
  const requestedQuery = request.query.trim().toLowerCase();
  const match = items.find((item) => {
    const query = stringValue(item.query)?.toLowerCase();
    return query === requestedQuery && item.retrieval_mode === request.retrieval_mode;
  });

  if (!match) {
    snapshotDisabled(
      "This public snapshot includes only curated precomputed searches. Run the full local stack for arbitrary live retrieval."
    );
  }

  const response = record(match.search_response);
  return {
    ...response,
    query_id: String(response.query_id || match.query_id || ""),
    trace_id: String(response.trace_id || match.trace_id || ""),
    query: String(response.query || match.query || request.query),
    retrieval_mode: (response.retrieval_mode || match.retrieval_mode || request.retrieval_mode) as SearchMode,
    top_k: Number(response.top_k || request.top_k),
    result_count: Number(response.result_count || match.result_count || 0),
    results: array(response.results || match.results)
  } as SearchResponse;
}

function traceToDetail(item: JsonRecord): TraceDetailResponse {
  const query = record(item.query);
  const traceJson = record(item.trace_json);
  return {
    trace_id: String(item.trace_id || ""),
    query_id: String(item.query_id || query.id || ""),
    query_text: String(query.text || traceJson.query || ""),
    retrieval_mode: (query.retrieval_mode || traceJson.retrieval_mode || "bm25") as SearchMode,
    index_version_id: stringValue(query.index_version_id) || stringValue(record(traceJson.index_version).id) || null,
    status: String(query.status || "completed"),
    total_latency_ms: typeof query.total_latency_ms === "number" ? query.total_latency_ms : null,
    trace_schema_version: stringValue(traceJson.trace_schema_version) || null,
    trace_json: traceJson,
    ranking_summary: record(traceJson.ranking_summary),
    candidates: array<TraceCandidateItem>(item.candidates),
    candidates_by_source: record(item.candidates_by_source) as Record<string, TraceCandidateItem[]>,
    created_at: stringValue(item.created_at) || null
  };
}

export async function getSnapshotTraceList(params: {
  retrievalMode?: SearchMode | "all";
  status?: string | "all";
  limit?: number;
  offset?: number;
} = {}): Promise<TraceListResponse> {
  const data = await fetchSnapshotFile<{ items?: JsonRecord[] }>("traces.json");
  let items = array<JsonRecord>(data.items).map((item) => {
    const detail = traceToDetail(item);
    return {
      trace_id: detail.trace_id,
      query_id: detail.query_id,
      query_text: detail.query_text,
      retrieval_mode: detail.retrieval_mode,
      status: detail.status,
      total_latency_ms: detail.total_latency_ms,
      result_count: detail.candidates?.length ?? null,
      created_at: detail.created_at
    };
  });
  if (params.retrievalMode && params.retrievalMode !== "all") {
    items = items.filter((item) => item.retrieval_mode === params.retrievalMode);
  }
  if (params.status && params.status !== "all") {
    items = items.filter((item) => item.status === params.status);
  }
  return page(items, params);
}

export async function getSnapshotTrace(traceId: string): Promise<TraceDetailResponse> {
  const data = await fetchSnapshotFile<{ items?: JsonRecord[] }>("traces.json");
  const match = array<JsonRecord>(data.items).find((item) => item.trace_id === traceId);
  if (!match) {
    throw new Error(`Trace ${traceId} is not included in the public snapshot.`);
  }
  return traceToDetail(match);
}

export async function getSnapshotTraceCandidates(
  traceId: string,
  params: { source?: string; limit?: number; offset?: number } = {}
): Promise<TraceCandidateListResponse> {
  const trace = await getSnapshotTrace(traceId);
  let items = trace.candidates || [];
  if (params.source) {
    items = items.filter((item) => item.source === params.source);
  }
  return page(items, params);
}

export async function getSnapshotEvaluationRuns(params: { status?: string | "all"; limit?: number; offset?: number } = {}): Promise<EvaluationRunListResponse> {
  const data = await fetchSnapshotFile<{ runs?: EvaluationRunDetail[] }>("evaluations.json");
  let items = array<EvaluationRunDetail>(data.runs);
  if (params.status && params.status !== "all") {
    items = items.filter((item) => item.status === params.status);
  }
  return page(items, params);
}

export async function getSnapshotEvaluationRun(runId: string): Promise<EvaluationRunDetail> {
  const runs = await getSnapshotEvaluationRuns({ limit: 1000, offset: 0 });
  const match = runs.items.find((item) => item.id === runId);
  if (!match) {
    throw new Error(`Evaluation run ${runId} is not included in the public snapshot.`);
  }
  return match;
}

export async function getSnapshotEvaluationRunResults(
  runId: string,
  params: { limit?: number; offset?: number; failedOnly?: boolean } = {}
): Promise<EvaluationQueryResultListResponse> {
  const data = await fetchSnapshotFile<{ query_results?: EvaluationQueryResultListResponse["items"] }>("evaluations.json");
  let items = array<EvaluationQueryResultListResponse["items"][number]>(data.query_results).filter(
    (item) => item.evaluation_run_id === runId
  );
  if (params.failedOnly) {
    items = items.filter((item) => Boolean(item.error_message));
  }
  return page(items, params);
}

export async function getSnapshotEvaluationRunReport(runId: string): Promise<EvaluationReportResponse> {
  const data = await fetchSnapshotFile<{ reports?: JsonRecord[] }>("evaluations.json");
  const report = array<JsonRecord>(data.reports).find((item) => item.evaluation_run_id === runId);
  if (!report) {
    return {
      evaluation_run_id: runId,
      report_path: null,
      report_format: null,
      summary_json: {},
      report_json: null,
      warning: "Report JSON is not included in the public snapshot."
    };
  }
  return {
    evaluation_run_id: runId,
    report_path: stringValue(report.report_path) || null,
    report_format: stringValue(report.report_format) || null,
    summary_json: record(report.summary_json),
    report_json: record(report.report_json),
    warning: null
  };
}

export async function getSnapshotExperimentConfigs(params: { retrievalMode?: SearchMode | "all"; isDefault?: boolean | null; limit?: number; offset?: number } = {}): Promise<ExperimentConfigListResponse> {
  const data = await fetchSnapshotFile<{ configs?: ExperimentConfigListResponse["items"] }>("experiments.json");
  let items = array<ExperimentConfigListResponse["items"][number]>(data.configs);
  if (params.retrievalMode && params.retrievalMode !== "all") {
    items = items.filter((item) => item.retrieval_mode === params.retrievalMode);
  }
  if (params.isDefault !== undefined && params.isDefault !== null) {
    items = items.filter((item) => Boolean(item.is_default) === params.isDefault);
  }
  return page(items, params);
}

export async function getSnapshotExperimentMatrix() {
  return fetchSnapshotFile<JsonRecord>("experiments.json");
}

export async function getSnapshotIndexStatus(): Promise<IndexStatusResponse> {
  return fetchSnapshotFile<IndexStatusResponse>("index-status.json");
}

export async function getSnapshotIndexVersions(params: { status?: string | "all"; limit?: number; offset?: number } = {}): Promise<IndexVersionListResponse> {
  const status = await getSnapshotIndexStatus();
  let items = status.latest_index_versions || [];
  if (params.status && params.status !== "all") {
    items = items.filter((item) => item.status === params.status);
  }
  return page(items, params);
}

export async function getSnapshotIndexVersion(id: string): Promise<IndexVersionItem> {
  const versions = await getSnapshotIndexVersions({ limit: 1000, offset: 0 });
  const match = versions.items.find((item) => item.id === id);
  if (!match) {
    throw new Error(`Index version ${id} is not included in the public snapshot.`);
  }
  return match;
}

export async function getSnapshotIndexJobs(params: { indexVersionId?: string; jobType?: string; status?: string | "all"; limit?: number; offset?: number } = {}): Promise<IndexJobListResponse> {
  const data = await fetchSnapshotFile<JsonRecord>("index-status.json");
  let items = array<IndexJobListResponse["items"][number]>(data.latest_index_jobs);
  if (params.indexVersionId) {
    items = items.filter((item) => item.index_version_id === params.indexVersionId);
  }
  if (params.jobType) {
    items = items.filter((item) => item.job_type === params.jobType);
  }
  if (params.status && params.status !== "all") {
    items = items.filter((item) => item.status === params.status);
  }
  return page(items, params);
}

export function getSnapshotOpenSearchHealth(): OpenSearchHealthResponse {
  return {
    status: "snapshot_only",
    url: "local full stack only",
    cluster_name: null,
    version: null,
    error: "OpenSearch is not hosted in public snapshot mode."
  };
}

export function getSnapshotQdrantHealth(): QdrantHealthResponse {
  return {
    status: "snapshot_only",
    url: "local full stack only",
    version: null,
    collections_count: null,
    error: "Qdrant is not hosted in public snapshot mode."
  };
}

export async function getSnapshotDatasets(): Promise<DatasetListResponse> {
  const data = await fetchSnapshotFile<JsonRecord>("datasets.json");
  const items = array<DatasetListResponse extends { items: infer T } ? T extends unknown[] ? T[number] : never : never>(data.datasets);
  return { total: items.length, limit: items.length, offset: 0, items } as DatasetListResponse;
}

export async function getSnapshotDatasetStats(datasetId?: string): Promise<DatasetStatsResponse> {
  const datasets = await getSnapshotDatasets();
  const items = Array.isArray(datasets) ? datasets : datasets.items || [];
  const match = datasetId ? items.find((item) => item.id === datasetId) : items[0];
  if (!match) {
    throw new Error("Dataset is not included in the public snapshot.");
  }
  return match as DatasetStatsResponse;
}

async function sampleFile<T>(fileName: SnapshotFileName): Promise<T[]> {
  const data = await fetchSnapshotFile<{ items?: T[] }>(fileName);
  return array<T>(data.items);
}

export async function getSnapshotDocuments(params: { datasetId?: string; limit?: number; offset?: number } = {}): Promise<DocumentListResponse> {
  let items = await sampleFile<DocumentListResponse["items"][number]>("documents-sample.json");
  if (params.datasetId) {
    items = items.filter((item) => item.dataset_id === params.datasetId);
  }
  return page(items, params);
}

export async function getSnapshotDocument(documentId: string): Promise<DocumentDetailResponse> {
  const docs = await getSnapshotDocuments({ limit: 1000, offset: 0 });
  const match = docs.items.find((item) => item.id === documentId);
  if (!match) {
    throw new Error(`Document ${documentId} is not included in the public snapshot sample.`);
  }
  return { ...match, text: match.text || match.text_preview || "", chunk_count: null, chunks_preview: [] };
}

export async function getSnapshotChunks(params: { datasetId?: string; documentId?: string; chunkingStrategy?: string; limit?: number; offset?: number } = {}): Promise<ChunkListResponse> {
  let items = await sampleFile<ChunkListResponse["items"][number]>("chunks-sample.json");
  if (params.datasetId) {
    items = items.filter((item) => item.dataset_id === params.datasetId);
  }
  if (params.documentId) {
    items = items.filter((item) => item.document_id === params.documentId);
  }
  if (params.chunkingStrategy) {
    items = items.filter((item) => item.chunking_strategy === params.chunkingStrategy);
  }
  return page(items, params);
}

export async function getSnapshotChunk(chunkId: string): Promise<ChunkDetailResponse> {
  const chunks = await getSnapshotChunks({ limit: 1000, offset: 0 });
  const match = chunks.items.find((item) => item.id === chunkId);
  if (!match) {
    throw new Error(`Chunk ${chunkId} is not included in the public snapshot sample.`);
  }
  return { ...match, text: match.text || match.text_preview || "" };
}

export async function getSnapshotBenchmarkQueries(params: { datasetId?: string; split?: string; limit?: number; offset?: number } = {}): Promise<BenchmarkQueryListResponse> {
  let items = await sampleFile<BenchmarkQueryListResponse["items"][number]>("benchmark-queries-sample.json");
  if (params.datasetId) {
    items = items.filter((item) => item.dataset_id === params.datasetId);
  }
  if (params.split) {
    items = items.filter((item) => item.split === params.split);
  }
  return page(items, params);
}

export async function getSnapshotBenchmarkQuery(queryId: string): Promise<BenchmarkQueryDetailResponse> {
  const queries = await getSnapshotBenchmarkQueries({ limit: 1000, offset: 0 });
  const match = queries.items.find((item) => item.id === queryId);
  if (!match) {
    throw new Error(`Benchmark query ${queryId} is not included in the public snapshot sample.`);
  }
  return { ...match, relevance_judgment_count: null };
}

export async function getSnapshotRelevanceJudgments(params: { datasetId?: string; queryId?: string; documentId?: string; queryExternalId?: string; documentExternalId?: string; limit?: number; offset?: number } = {}): Promise<RelevanceJudgmentListResponse> {
  let items = await sampleFile<RelevanceJudgmentListResponse["items"][number]>("relevance-judgments-sample.json");
  if (params.datasetId) {
    items = items.filter((item) => item.dataset_id === params.datasetId);
  }
  if (params.queryId) {
    items = items.filter((item) => item.query_id === params.queryId);
  }
  if (params.documentId) {
    items = items.filter((item) => item.document_id === params.documentId);
  }
  if (params.queryExternalId) {
    items = items.filter((item) => item.query_external_id === params.queryExternalId);
  }
  if (params.documentExternalId) {
    items = items.filter((item) => item.document_external_id === params.documentExternalId);
  }
  return page(items, params);
}

export async function getSnapshotSavedQueries(params: { source?: string; datasetId?: string; limit?: number; offset?: number } = {}): Promise<SavedQueryListResponse> {
  const data = await fetchSnapshotFile<{ saved_queries?: SavedQueryListResponse["items"] }>("replay.json");
  let items = array<SavedQueryListResponse["items"][number]>(data.saved_queries);
  if (params.source && params.source !== "all") {
    items = items.filter((item) => item.source === params.source);
  }
  if (params.datasetId) {
    items = items.filter((item) => item.dataset_id === params.datasetId);
  }
  return page(items, params);
}

export async function getSnapshotSavedQuery(id: string): Promise<SavedQueryDetail> {
  const queries = await getSnapshotSavedQueries({ limit: 1000, offset: 0 });
  const match = queries.items.find((item) => item.id === id);
  if (!match) {
    throw new Error(`Saved query ${id} is not included in the public snapshot.`);
  }
  return match;
}

export async function getSnapshotQueryReplays(params: { savedQueryId?: string; status?: string | "all"; limit?: number; offset?: number } = {}): Promise<QueryReplayListResponse> {
  const data = await fetchSnapshotFile<{ query_replays?: QueryReplayListResponse["items"] }>("replay.json");
  let items = array<QueryReplayListResponse["items"][number]>(data.query_replays);
  if (params.savedQueryId) {
    items = items.filter((item) => item.saved_query_id === params.savedQueryId);
  }
  if (params.status && params.status !== "all") {
    items = items.filter((item) => item.status === params.status);
  }
  return page(items, params);
}

export async function getSnapshotQueryReplay(replayId: string): Promise<QueryReplayDetail> {
  const replays = await getSnapshotQueryReplays({ limit: 1000, offset: 0 });
  const match = replays.items.find((item) => item.id === replayId);
  if (!match) {
    throw new Error(`Query replay ${replayId} is not included in the public snapshot.`);
  }
  return match;
}

export async function getSnapshotSystemHealth() {
  return fetchSnapshotFile<JsonRecord>("system.json");
}

export async function getSnapshotSystemEvents(params: { eventType?: string; severity?: string; limit?: number; offset?: number } = {}): Promise<SystemEventListResponse> {
  const data = await getSnapshotSystemHealth();
  let items = array<SystemEventListResponse["items"][number]>(data.system_events);
  if (params.severity && params.severity !== "all") {
    items = items.filter((item) => item.severity === params.severity);
  }
  if (params.eventType) {
    const eventType = params.eventType.toLowerCase();
    items = items.filter((item) => item.event_type.toLowerCase().includes(eventType));
  }
  return page(items, params);
}

export function getSnapshotApiHealth() {
  return {
    status: "snapshot",
    service: "Vercel frontend",
    version: "static snapshot",
    app_mode: "snapshot"
  };
}

export function getSnapshotDbHealth() {
  return {
    status: "snapshot",
    database: "Neon schema and static exported data",
    error: null
  };
}

export function getSnapshotQueueStatus() {
  return {
    queue: "local full stack only",
    job_count: 0,
    status: "disabled",
    error: "Redis/RQ is not hosted in public snapshot mode."
  };
}

export function getSnapshotWorkerHeartbeats() {
  return {
    total: 0,
    limit: 0,
    offset: 0,
    items: []
  };
}

export function getSnapshotModelStatus(modelName: string) {
  return {
    model_name: modelName,
    device: "local full stack only",
    loaded: false,
    cache_dir: null,
    error: "Models are not loaded in public snapshot mode."
  };
}
