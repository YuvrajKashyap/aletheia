import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { API_BASE_URL } from "@/lib/config";
import {
  getDatasets,
  getDbHealth,
  getExperimentConfigs,
  getHealth,
  getIndexStatus,
  getLatestEvaluationRuns,
  getOpenSearchHealth,
  getQdrantHealth,
  getRecentTraces,
  getSavedQueries
} from "@/lib/api/overview";

export const dynamic = "force-dynamic";

type LoadResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string };

async function load<T>(promise: Promise<T>): Promise<LoadResult<T>> {
  try {
    return { ok: true, data: await promise };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : "Request failed"
    };
  }
}

function tone(status?: string | null): "neutral" | "good" | "warn" | "bad" {
  const normalized = (status || "").toLowerCase();
  if (["ok", "healthy", "ready", "completed", "active"].includes(normalized)) {
    return "good";
  }
  if (["degraded", "running", "building"].includes(normalized)) {
    return "warn";
  }
  if (["error", "failed", "unhealthy"].includes(normalized)) {
    return "bad";
  }
  return "neutral";
}

function StatusCard({
  title,
  result,
  detail
}: {
  title: string;
  result: LoadResult<{ status?: string; error?: string | null }>;
  detail?: string;
}) {
  if (!result.ok) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>Backend request failed</CardDescription>
        </CardHeader>
        <CardContent>
          <Badge tone="bad">error</Badge>
          <p className="mt-3 text-sm text-red-300">{result.error}</p>
        </CardContent>
      </Card>
    );
  }

  const status = result.data.status || "unknown";
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{detail || "Live backend status"}</CardDescription>
      </CardHeader>
      <CardContent>
        <Badge tone={tone(status)}>{status}</Badge>
        {result.data.error ? <p className="mt-3 text-sm text-red-300">{result.data.error}</p> : null}
      </CardContent>
    </Card>
  );
}

function ErrorBlock({ title, message }: { title: string; message: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>Data unavailable</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-red-300">{message}</p>
      </CardContent>
    </Card>
  );
}

function formatMetric(value?: number | null) {
  return typeof value === "number" ? value.toFixed(3) : "unavailable";
}

function evaluationMode(config?: Record<string, unknown>) {
  const value = config?.retrieval_mode;
  return typeof value === "string" ? value : "mode unknown";
}

function shortId(value?: string | null) {
  return value ? value.slice(0, 8) : "unavailable";
}

export default async function OverviewPage() {
  const [health, dbHealth, openSearch, qdrant, indexStatus, evalRuns, configs, traces, datasets, savedQueries] =
    await Promise.all([
      load(getHealth()),
      load(getDbHealth()),
      load(getOpenSearchHealth()),
      load(getQdrantHealth()),
      load(getIndexStatus()),
      load(getLatestEvaluationRuns(5)),
      load(getExperimentConfigs(8)),
      load(getRecentTraces(5)),
      load(getDatasets()),
      load(getSavedQueries(5))
    ]);

  const activeIndex = indexStatus.ok ? indexStatus.data.active_index_version : null;
  const evaluationItems = evalRuns.ok ? evalRuns.data.items || [] : [];
  const configItems = configs.ok ? configs.data.items || [] : [];
  const traceItems = traces.ok ? traces.data.items || [] : [];
  const datasetItems = datasets.ok ? (Array.isArray(datasets.data) ? datasets.data : datasets.data.items || []) : [];
  const savedQueryItems = savedQueries.ok ? savedQueries.data.items || [] : [];

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="space-y-3">
          <Badge tone="neutral">Aletheia</Badge>
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-white">
              Hybrid Retrieval, Reranking & Evaluation Platform
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Frontend foundation connected to the real FastAPI backend. Values below come from live
              API responses or show explicit unavailable states.
            </p>
          </div>
          <div className="font-mono text-xs text-slate-500">Backend: {API_BASE_URL}</div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatusCard title="API" result={health} detail={health.ok ? health.data.service : undefined} />
          <StatusCard title="Postgres" result={dbHealth} detail={dbHealth.ok ? dbHealth.data.database : undefined} />
          <StatusCard title="OpenSearch" result={openSearch} detail={openSearch.ok ? openSearch.data.url : undefined} />
          <StatusCard title="Qdrant" result={qdrant} detail={qdrant.ok ? qdrant.data.url : undefined} />
        </section>

        <section className="grid gap-4 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <CardHeader>
              <CardTitle>Active Index</CardTitle>
              <CardDescription>Versioned retrieval assets reported by FastAPI</CardDescription>
            </CardHeader>
            <CardContent>
              {!indexStatus.ok ? (
                <p className="text-sm text-red-300">{indexStatus.error}</p>
              ) : activeIndex ? (
                <div className="grid gap-3 text-sm md:grid-cols-2">
                  <div>
                    <div className="text-slate-500">Name</div>
                    <div className="font-medium text-slate-100">{activeIndex.name || "unavailable"}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">ID</div>
                    <div className="font-mono text-slate-300">{activeIndex.id || "unavailable"}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Chunks</div>
                    <div className="text-slate-100">{activeIndex.chunk_count ?? "unavailable"}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Vectors</div>
                    <div className="text-slate-100">{activeIndex.vector_count ?? "unavailable"}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Lexical index</div>
                    <div className="font-mono text-slate-300">{activeIndex.lexical_index_name || "unavailable"}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Vector collection</div>
                    <div className="font-mono text-slate-300">
                      {activeIndex.vector_collection_name || "unavailable"}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-400">No active index reported by the backend.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Datasets</CardTitle>
              <CardDescription>Loaded corpus and qrels inventory</CardDescription>
            </CardHeader>
            <CardContent>
              {!datasets.ok ? (
                <p className="text-sm text-red-300">{datasets.error}</p>
              ) : (
                <div className="space-y-3">
                  <div className="text-2xl font-semibold text-white">{datasetItems.length}</div>
                  {datasetItems.map((dataset) => (
                    <div key={dataset.id} className="rounded-md border border-slate-800 p-3">
                      <div className="font-medium text-slate-100">{dataset.name || "unnamed dataset"}</div>
                      <div className="mt-1 text-xs text-slate-500">version {dataset.version || "unknown"}</div>
                      <div className="mt-2 grid grid-cols-3 gap-2 text-xs text-slate-400">
                        <span>docs {dataset.document_count ?? "n/a"}</span>
                        <span>queries {dataset.benchmark_query_count ?? "n/a"}</span>
                        <span>qrels {dataset.relevance_judgment_count ?? "n/a"}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </section>

        {!evalRuns.ok ? (
          <ErrorBlock title="Latest Evaluation Runs" message={evalRuns.error} />
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Latest Evaluation Runs</CardTitle>
              <CardDescription>Real qrels-backed evaluation results from the backend</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Mode</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Recall@10</TableHead>
                    <TableHead>MRR@10</TableHead>
                    <TableHead>NDCG@10</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {evaluationItems.length ? (
                    evaluationItems.map((run) => (
                      <TableRow key={run.id}>
                        <TableCell className="font-medium text-slate-100">{run.name || "unnamed run"}</TableCell>
                        <TableCell>{evaluationMode(run.config_json)}</TableCell>
                        <TableCell>
                          <Badge tone={tone(run.status)}>{run.status || "unknown"}</Badge>
                        </TableCell>
                        <TableCell>{formatMetric(run.recall_at_10)}</TableCell>
                        <TableCell>{formatMetric(run.mrr_at_10)}</TableCell>
                        <TableCell>{formatMetric(run.ndcg_at_10)}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6}>No evaluation runs returned by the backend.</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        <section className="grid gap-4 xl:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Experiment Configs</CardTitle>
              <CardDescription>{configs.ok ? `${configs.data.total ?? configItems.length} configs` : "Data unavailable"}</CardDescription>
            </CardHeader>
            <CardContent>
              {!configs.ok ? (
                <p className="text-sm text-red-300">{configs.error}</p>
              ) : (
                <div className="space-y-2">
                  {configItems.map((config) => (
                    <div key={config.id} className="flex items-center justify-between rounded-md border border-slate-800 px-3 py-2">
                      <div>
                        <div className="text-sm font-medium text-slate-100">{config.name || "unnamed config"}</div>
                        <div className="text-xs text-slate-500">{config.retrieval_mode || "mode unknown"}</div>
                      </div>
                      {config.is_default ? <Badge>default</Badge> : null}
                    </div>
                  ))}
                  {!configItems.length ? <p className="text-sm text-slate-400">No configs returned.</p> : null}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Traces</CardTitle>
              <CardDescription>{traces.ok ? `${traces.data.total ?? traceItems.length} traces` : "Data unavailable"}</CardDescription>
            </CardHeader>
            <CardContent>
              {!traces.ok ? (
                <p className="text-sm text-red-300">{traces.error}</p>
              ) : (
                <div className="space-y-2">
                  {traceItems.map((trace) => (
                    <div key={trace.trace_id} className="rounded-md border border-slate-800 px-3 py-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-mono text-xs text-slate-300">{shortId(trace.trace_id)}</span>
                        <Badge tone={tone(trace.status)}>{trace.status || "unknown"}</Badge>
                      </div>
                      <div className="mt-1 truncate text-xs text-slate-500">{trace.query_text || "query unavailable"}</div>
                    </div>
                  ))}
                  {!traceItems.length ? <p className="text-sm text-slate-400">No traces returned.</p> : null}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Saved Queries</CardTitle>
              <CardDescription>{savedQueries.ok ? `${savedQueries.data.total ?? savedQueryItems.length} saved queries` : "Data unavailable"}</CardDescription>
            </CardHeader>
            <CardContent>
              {!savedQueries.ok ? (
                <p className="text-sm text-red-300">{savedQueries.error}</p>
              ) : (
                <div className="space-y-2">
                  {savedQueryItems.map((query) => (
                    <div key={query.id} className="rounded-md border border-slate-800 px-3 py-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium text-slate-100">{query.name || "unnamed query"}</span>
                        <Badge>{query.source || "source unknown"}</Badge>
                      </div>
                      <div className="mt-1 line-clamp-2 text-xs text-slate-500">{query.text || "text unavailable"}</div>
                    </div>
                  ))}
                  {!savedQueryItems.length ? <p className="text-sm text-slate-400">No saved queries returned.</p> : null}
                </div>
              )}
            </CardContent>
          </Card>
        </section>
      </div>
    </AppShell>
  );
}
