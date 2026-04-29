import Link from "next/link";

import { getEvaluationRunModeLabel } from "@/components/evaluations/evaluation-run-labels";
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
import { getSnapshotManifest, getSnapshotOverview } from "@/lib/api/snapshot";
import { getSystemEvents } from "@/lib/api/system";
import type { EvaluationRunItem } from "@/lib/api/types";
import { isSnapshotMode } from "@/lib/demo-mode";
import { formatMetric, formatNumber, formatShortId } from "@/lib/format";

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
  if (["degraded", "running", "building", "warning", "warn"].includes(normalized)) {
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

function overviewEvaluationMode(run: EvaluationRunItem) {
  const label = getEvaluationRunModeLabel(run);
  return label === "Unknown mode" ? "Unavailable" : label;
}

function shortId(value?: string | null) {
  return formatShortId(value).toLowerCase();
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function asArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === "object") as Record<string, unknown>[] : [];
}

function asString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function SnapshotOverview({
  manifest,
  overview
}: {
  manifest: LoadResult<Record<string, unknown>>;
  overview: LoadResult<Record<string, unknown>>;
}) {
  const manifestData = manifest.ok ? manifest.data : {};
  const overviewData = overview.ok ? overview.data : {};
  const counts = asRecord(overviewData.counts);
  const activeIndex = asRecord(overviewData.active_index);
  const datasets = asArray(overviewData.datasets);
  const latestEvaluations = asArray(overviewData.latest_evaluations);
  const experimentConfigs = asArray(overviewData.experiment_configs);
  const recentTraces = asArray(overviewData.recent_traces);
  const systemEvents = asArray(overviewData.system_events);

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
              Public snapshot overview built from real precomputed traces, evaluations, index metadata, datasets, and replay outputs
              exported from the full local Aletheia pipeline.
            </p>
          </div>
          <div className="font-mono text-xs text-slate-500">Demo mode: snapshot</div>
        </section>

        {!manifest.ok ? <ErrorBlock title="Snapshot Manifest" message={manifest.error} /> : null}
        {!overview.ok ? <ErrorBlock title="Snapshot Overview" message={overview.error} /> : null}

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card>
            <CardHeader>
              <CardTitle>Snapshot Source</CardTitle>
              <CardDescription>Static public demo data</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge tone={manifestData.generated === true ? "good" : "warn"}>
                {manifestData.generated === true ? "generated" : "not generated"}
              </Badge>
              <p className="mt-3 text-xs text-slate-400">{asString(manifestData.source) || "source unavailable"}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
              <CardDescription>Real corpus rows</CardDescription>
            </CardHeader>
            <CardContent className="text-2xl font-semibold text-white">{formatNumber(asNumber(counts.documents))}</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Traces</CardTitle>
              <CardDescription>Stored query traces</CardDescription>
            </CardHeader>
            <CardContent className="text-2xl font-semibold text-white">{formatNumber(asNumber(counts.traces))}</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Evaluation Runs</CardTitle>
              <CardDescription>Real qrels-backed runs</CardDescription>
            </CardHeader>
            <CardContent className="text-2xl font-semibold text-white">
              {formatNumber(asNumber(counts.evaluation_runs))}
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-4 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <CardHeader>
              <CardTitle>Active Index</CardTitle>
              <CardDescription>Exported index metadata from the local full stack</CardDescription>
            </CardHeader>
            <CardContent>
              {Object.keys(activeIndex).length ? (
                <div className="grid gap-3 text-sm md:grid-cols-2">
                  <div>
                    <div className="text-slate-500">Name</div>
                    <div className="font-medium text-slate-100">{asString(activeIndex.name) || "Unavailable"}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Status</div>
                    <Badge tone={tone(asString(activeIndex.status))}>{asString(activeIndex.status) || "unknown"}</Badge>
                  </div>
                  <div>
                    <div className="text-slate-500">Documents</div>
                    <div className="text-slate-100">{formatNumber(asNumber(activeIndex.document_count))}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Chunks</div>
                    <div className="text-slate-100">{formatNumber(asNumber(activeIndex.chunk_count))}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Vectors</div>
                    <div className="text-slate-100">{formatNumber(asNumber(activeIndex.vector_count))}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Lexical index</div>
                    <div className="font-mono text-slate-300">{asString(activeIndex.lexical_index_name) || "Unavailable"}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Vector collection</div>
                    <div className="font-mono text-slate-300">
                      {asString(activeIndex.vector_collection_name) || "Unavailable"}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-400">No active index was included in the snapshot.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Datasets</CardTitle>
              <CardDescription>Exported corpus inventory</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-2xl font-semibold text-white">{datasets.length}</div>
              {datasets.map((dataset) => (
                <div key={asString(dataset.id) || asString(dataset.name) || "dataset"} className="rounded-md border border-slate-800 p-3">
                  <div className="font-medium text-slate-100">{asString(dataset.name) || "unnamed dataset"}</div>
                  <div className="mt-1 text-xs text-slate-500">version {asString(dataset.version) || "unknown"}</div>
                  <div className="mt-2 grid grid-cols-3 gap-2 text-xs text-slate-400">
                    <span>docs {formatNumber(asNumber(dataset.document_count))}</span>
                    <span>chunks {formatNumber(asNumber(dataset.chunk_count))}</span>
                    <span>qrels {formatNumber(asNumber(dataset.relevance_judgment_count))}</span>
                  </div>
                  <div className="mt-1 text-xs text-slate-400">
                    queries {formatNumber(asNumber(dataset.benchmark_query_count))}
                  </div>
                </div>
              ))}
              {!datasets.length ? <p className="text-sm text-slate-400">No dataset rows were included in the snapshot.</p> : null}
            </CardContent>
          </Card>
        </section>

        <Card>
          <CardHeader>
            <CardTitle>Latest Evaluation Runs</CardTitle>
            <CardDescription>Real metrics exported from stored evaluation runs</CardDescription>
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
                {latestEvaluations.length ? (
                  latestEvaluations.map((run) => (
                    <TableRow key={asString(run.id) || asString(run.name) || "evaluation"}>
                      <TableCell className="font-medium text-slate-100">{asString(run.name) || "unnamed run"}</TableCell>
                      <TableCell>{overviewEvaluationMode(run as unknown as EvaluationRunItem)}</TableCell>
                      <TableCell>
                        <Badge tone={tone(asString(run.status))}>{asString(run.status) || "unknown"}</Badge>
                      </TableCell>
                      <TableCell>{formatMetric(asNumber(run.recall_at_10), 3)}</TableCell>
                      <TableCell>{formatMetric(asNumber(run.mrr_at_10), 3)}</TableCell>
                      <TableCell>{formatMetric(asNumber(run.ndcg_at_10), 3)}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6}>No evaluation runs were included in the snapshot.</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <section className="grid gap-4 xl:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Experiment Configs</CardTitle>
              <CardDescription>{experimentConfigs.length} configs in snapshot</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {experimentConfigs.map((config) => (
                <div key={asString(config.id) || asString(config.name) || "config"} className="rounded-md border border-slate-800 px-3 py-2">
                  <div className="text-sm font-medium text-slate-100">{asString(config.name) || "unnamed config"}</div>
                  <div className="text-xs text-slate-500">{asString(config.retrieval_mode) || "mode unavailable"}</div>
                </div>
              ))}
              {!experimentConfigs.length ? <p className="text-sm text-slate-400">No configs were included in the snapshot.</p> : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Traces</CardTitle>
              <CardDescription>{recentTraces.length} traces in snapshot</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {recentTraces.map((trace) => (
                <div key={asString(trace.trace_id) || "trace"} className="rounded-md border border-slate-800 px-3 py-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs text-slate-300">{shortId(asString(trace.trace_id))}</span>
                    <Badge tone={tone(asString(trace.status))}>{asString(trace.status) || "unknown"}</Badge>
                  </div>
                  <div className="mt-1 truncate text-xs text-slate-500">{asString(trace.query_text) || "query unavailable"}</div>
                </div>
              ))}
              {!recentTraces.length ? <p className="text-sm text-slate-400">No traces were included in the snapshot.</p> : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Replay</CardTitle>
              <CardDescription>Saved query and replay inventory</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-slate-500">Saved queries</div>
                <div className="text-2xl font-semibold text-white">{formatNumber(asNumber(overviewData.saved_query_count))}</div>
              </div>
              <div>
                <div className="text-slate-500">Query replays</div>
                <div className="text-2xl font-semibold text-white">{formatNumber(asNumber(overviewData.query_replay_count))}</div>
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-4 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <CardHeader>
              <CardTitle>Recent System Events</CardTitle>
              <CardDescription>Real exported backend events</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {systemEvents.map((event) => (
                <div key={asString(event.id) || "event"} className="grid gap-2 rounded-md border border-slate-800 px-3 py-2 text-sm md:grid-cols-[120px_1fr]">
                  <Badge tone={tone(asString(event.severity))}>{asString(event.severity) || "unknown"}</Badge>
                  <div>
                    <div className="font-medium text-slate-100">{asString(event.event_type) || "event type unavailable"}</div>
                    <div className="mt-1 text-xs text-slate-500">{asString(event.message) || "message unavailable"}</div>
                  </div>
                </div>
              ))}
              {!systemEvents.length ? <p className="text-sm text-slate-400">No system events were included in the snapshot.</p> : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Product Surfaces</CardTitle>
              <CardDescription>Snapshot pages continue to use real exported data as they are converted.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-2">
              {quickLinks.map((link) => (
                <Link
                  className="rounded-md border border-slate-800 px-3 py-2 text-sm text-slate-200 transition hover:border-cyan-700 hover:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-400/70"
                  href={link.href}
                  key={link.href}
                >
                  <div className="font-medium">{link.label}</div>
                  <div className="mt-1 text-xs text-slate-500">{link.description}</div>
                </Link>
              ))}
            </CardContent>
          </Card>
        </section>
      </div>
    </AppShell>
  );
}

export default async function OverviewPage() {
  if (isSnapshotMode()) {
    const [manifest, overview] = await Promise.all([
      load(getSnapshotManifest()),
      load(getSnapshotOverview())
    ]);
    return <SnapshotOverview manifest={manifest} overview={overview} />;
  }

  const [health, dbHealth, openSearch, qdrant, indexStatus, evalRuns, configs, traces, datasets, savedQueries, systemEvents] =
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
      load(getSavedQueries(5)),
      load(getSystemEvents({ limit: 5, offset: 0 }))
    ]);

  const activeIndex = indexStatus.ok ? indexStatus.data.active_index_version : null;
  const evaluationItems = evalRuns.ok ? evalRuns.data.items || [] : [];
  const configItems = configs.ok ? configs.data.items || [] : [];
  const traceItems = traces.ok ? traces.data.items || [] : [];
  const datasetItems = datasets.ok ? (Array.isArray(datasets.data) ? datasets.data : datasets.data.items || []) : [];
  const savedQueryItems = savedQueries.ok ? savedQueries.data.items || [] : [];
  const systemEventItems = systemEvents.ok ? systemEvents.data.items || [] : [];

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
              Integrated control surface for search, traces, evaluations, experiments, replay, indexes, datasets, and system health.
              Values below come from live API responses or show explicit unavailable states.
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
                    <div className="text-slate-500">Documents</div>
                    <div className="text-slate-100">{formatNumber(activeIndex.document_count)}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Chunks</div>
                    <div className="text-slate-100">{formatNumber(activeIndex.chunk_count)}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Vectors</div>
                    <div className="text-slate-100">{formatNumber(activeIndex.vector_count)}</div>
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
                        <span>docs {formatNumber(dataset.document_count)}</span>
                        <span>chunks {formatNumber(dataset.chunk_count)}</span>
                        <span>qrels {formatNumber(dataset.relevance_judgment_count)}</span>
                      </div>
                      <div className="mt-1 text-xs text-slate-400">queries {formatNumber(dataset.benchmark_query_count)}</div>
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
                        <TableCell>{overviewEvaluationMode(run)}</TableCell>
                        <TableCell>
                          <Badge tone={tone(run.status)}>{run.status || "unknown"}</Badge>
                        </TableCell>
                        <TableCell>{formatMetric(run.recall_at_10, 3)}</TableCell>
                        <TableCell>{formatMetric(run.mrr_at_10, 3)}</TableCell>
                        <TableCell>{formatMetric(run.ndcg_at_10, 3)}</TableCell>
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

        <section className="grid gap-4 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <CardHeader>
              <CardTitle>Recent System Events</CardTitle>
              <CardDescription>{systemEvents.ok ? `${systemEvents.data.total ?? systemEventItems.length} events available` : "Data unavailable"}</CardDescription>
            </CardHeader>
            <CardContent>
              {!systemEvents.ok ? (
                <p className="text-sm text-red-300">{systemEvents.error}</p>
              ) : (
                <div className="space-y-2">
                  {systemEventItems.map((event) => (
                    <div key={event.id} className="grid gap-2 rounded-md border border-slate-800 px-3 py-2 text-sm md:grid-cols-[120px_1fr_auto]">
                      <Badge tone={tone(event.severity)}>{event.severity || "unknown"}</Badge>
                      <div>
                        <div className="font-medium text-slate-100">{event.event_type || "event type unavailable"}</div>
                        <div className="mt-1 text-xs text-slate-500">{event.message || "message unavailable"}</div>
                      </div>
                      {event.trace_id ? (
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-mono text-xs text-slate-400">{shortId(event.trace_id)}</span>
                          <Link
                            className="inline-flex h-7 items-center rounded-md border border-cyan-800 bg-cyan-950/40 px-2 text-xs font-medium text-cyan-200 transition hover:border-cyan-500 hover:text-cyan-100 focus:outline-none focus:ring-2 focus:ring-cyan-400/70"
                            href={`/traces?traceId=${encodeURIComponent(event.trace_id)}`}
                          >
                            Open trace
                          </Link>
                        </div>
                      ) : null}
                    </div>
                  ))}
                  {!systemEventItems.length ? <p className="text-sm text-slate-400">No system events returned.</p> : null}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Product Surfaces</CardTitle>
              <CardDescription>Direct paths into the integrated retrieval platform.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-2">
              {quickLinks.map((link) => (
                <Link
                  className="rounded-md border border-slate-800 px-3 py-2 text-sm text-slate-200 transition hover:border-cyan-700 hover:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-400/70"
                  href={link.href}
                  key={link.href}
                >
                  <div className="font-medium">{link.label}</div>
                  <div className="mt-1 text-xs text-slate-500">{link.description}</div>
                </Link>
              ))}
            </CardContent>
          </Card>
        </section>
      </div>
    </AppShell>
  );
}

const quickLinks = [
  { href: "/search", label: "Search Lab", description: "Run BM25, dense, hybrid, and reranked retrieval." },
  { href: "/traces", label: "Query Traces", description: "Inspect trace stages, candidates, and rank movement." },
  { href: "/evaluations", label: "Evaluations", description: "Review qrels-backed metrics and per-query results." },
  { href: "/experiments", label: "Experiments", description: "Compare configs and latency versus quality tradeoffs." },
  { href: "/indexes", label: "Index Console", description: "Inspect index versions, jobs, and retrieval backends." },
  { href: "/datasets", label: "Dataset Browser", description: "Browse corpus documents, chunks, queries, and qrels." },
  { href: "/replay", label: "Replay Lab", description: "Replay saved queries and compare trace outputs." },
  { href: "/system", label: "System Health", description: "Check API, queue, workers, models, and events." }
];
