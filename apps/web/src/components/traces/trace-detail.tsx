import { ModePill } from "@/components/search/mode-pill";
import { RankMovementPanel } from "@/components/traces/rank-movement-panel";
import { TraceCandidateTable } from "@/components/traces/trace-candidate-table";
import { TraceJsonPanel } from "@/components/traces/trace-json-panel";
import { TraceRankingSummary } from "@/components/traces/trace-ranking-summary";
import { TraceStagePanel } from "@/components/traces/trace-stage-panel";
import { TraceStatusBadge } from "@/components/traces/trace-status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TraceDetailResponse } from "@/lib/api/types";

type TraceDetailProps = {
  trace: TraceDetailResponse;
};

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : undefined;
}

function getObject(source: Record<string, unknown>, key: string): Record<string, unknown> | undefined {
  return asRecord(source[key]);
}

function valueOrUnknown(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "unavailable";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  return String(value);
}

function formatMs(value?: number | null): string {
  return value === null || value === undefined ? "unavailable" : `${value.toFixed(1)} ms`;
}

export function TraceDetail({ trace }: TraceDetailProps) {
  const traceJson = trace.trace_json || {};
  const indexVersion = getObject(traceJson, "index_version") || {};
  const parameters = getObject(traceJson, "parameters") || {};
  const stages = getObject(traceJson, "stages");
  const rankingSummary =
    trace.ranking_summary && Object.keys(trace.ranking_summary).length > 0
      ? trace.ranking_summary
      : getObject(traceJson, "ranking_summary");
  const requestId = traceJson.request_id;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Trace detail</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <ModePill mode={trace.retrieval_mode} />
              <TraceStatusBadge status={trace.status} />
              <span className="text-sm text-slate-400">{formatMs(trace.total_latency_ms)}</span>
            </div>
            <p className="text-base font-medium leading-7 text-slate-100">{trace.query_text}</p>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <Metadata label="trace_id" value={trace.trace_id} />
            <Metadata label="query_id" value={trace.query_id} />
            <Metadata label="request_id" value={requestId} />
            <Metadata label="trace schema" value={trace.trace_schema_version} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Index version</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            <Metadata label="index version id" value={trace.index_version_id || indexVersion.id} />
            <Metadata label="name" value={indexVersion.name} />
            <Metadata label="lexical index" value={indexVersion.lexical_index_name} />
            <Metadata label="vector collection" value={indexVersion.vector_collection_name} />
            <Metadata label="embedding model" value={indexVersion.embedding_model} />
            <Metadata label="embedding dimension" value={indexVersion.embedding_dimension} />
            <Metadata label="chunking strategy" value={indexVersion.chunking_strategy} />
            <Metadata label="chunking version" value={indexVersion.chunking_version} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
            {["top_k", "candidate_k", "bm25_candidate_k", "dense_candidate_k", "hybrid_candidate_k", "rerank_top_n", "rrf_k"].map(
              (key) => (
                <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2" key={key}>
                  <div className="text-[11px] uppercase tracking-wide text-slate-500">{key}</div>
                  <div className="mt-1 font-mono text-sm text-slate-100">{valueOrUnknown(parameters[key])}</div>
                </div>
              )
            )}
          </div>
        </CardContent>
      </Card>

      <TraceStagePanel stages={stages} />
      <TraceRankingSummary summary={rankingSummary} />
      {trace.retrieval_mode === "hybrid_rerank" ? <RankMovementPanel rankingSummary={rankingSummary} /> : null}
      <TraceCandidateTable candidates={trace.candidates || []} candidatesBySource={trace.candidates_by_source} />
      <TraceJsonPanel traceJson={traceJson} rankingSummary={rankingSummary} />
    </div>
  );
}

function Metadata({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="min-w-0 rounded-md border border-slate-800 bg-slate-950 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 select-all break-all font-mono text-xs text-slate-200">{valueOrUnknown(value)}</div>
    </div>
  );
}
