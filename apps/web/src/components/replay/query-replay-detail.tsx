import Link from "next/link";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ReplayDocumentLists } from "@/components/replay/replay-document-lists";
import { ReplayJsonPanel } from "@/components/replay/replay-json-panel";
import { ReplayMetricsCards } from "@/components/replay/replay-metrics-cards";
import { ReplayStatusBadge } from "@/components/replay/replay-status-badge";
import type { QueryReplayDetail } from "@/lib/api/types";

function value(comparison: Record<string, unknown> | undefined, key: string) {
  const item = comparison?.[key];
  return typeof item === "string" || typeof item === "number" ? String(item) : "Unavailable";
}

function objectValue(comparison: Record<string, unknown> | undefined, key: string): Record<string, unknown> | undefined {
  const item = comparison?.[key];
  return item && typeof item === "object" && !Array.isArray(item) ? (item as Record<string, unknown>) : undefined;
}

export function QueryReplayDetailPanel({ replay }: { replay: QueryReplayDetail | null }) {
  if (!replay) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Select a replay run to inspect metrics and trace links.</p>;
  }

  const comparison = replay.comparison_json;
  const rankComparison = objectValue(comparison, "rank_comparison");

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center gap-3">
            <CardTitle>Replay detail</CardTitle>
            <ReplayStatusBadge status={replay.status} />
          </div>
          <CardDescription>{value(comparison, "retrieval_mode")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="rounded-md border border-slate-800 bg-slate-950 p-3 text-sm text-slate-300">
            {value(comparison, "query_text")}
          </p>
          <div className="grid gap-3 text-sm md:grid-cols-2">
            <Field label="Query replay ID" value={replay.id} mono />
            <Field label="Saved query ID" value={replay.saved_query_id || "Unavailable"} mono />
            <TraceField label="Target trace" traceId={replay.target_trace_id} />
            <TraceField label="Source trace" traceId={replay.source_trace_id} />
            <Field label="Experiment config ID" value={replay.experiment_config_id || "Unavailable"} mono />
            <Field label="Index version ID" value={replay.index_version_id || "Unavailable"} mono />
          </div>
          {replay.error_message ? <p className="rounded-md border border-red-900/70 p-3 text-sm text-red-300">{replay.error_message}</p> : null}
        </CardContent>
      </Card>

      <ReplayMetricsCards comparison={comparison} />
      <ReplayDocumentLists comparison={comparison} />

      <Card>
        <CardHeader>
          <CardTitle>Rank comparison</CardTitle>
          <CardDescription>Trace-to-trace rank movement when source trace data exists.</CardDescription>
        </CardHeader>
        <CardContent>
          {rankComparison ? (
            <pre className="max-h-72 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
              {JSON.stringify(rankComparison, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-slate-400">Unavailable</p>
          )}
        </CardContent>
      </Card>

      <ReplayJsonPanel title="Comparison JSON" value={comparison} />
    </div>
  );
}

function Field({ label, value: fieldValue, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <div className="text-slate-500">{label}</div>
      <div className={mono ? "break-all font-mono text-xs text-slate-300" : "text-slate-300"}>{fieldValue}</div>
    </div>
  );
}

function TraceField({ label, traceId }: { label: string; traceId?: string | null }) {
  return (
    <div>
      <div className="text-slate-500">{label}</div>
      {traceId ? (
        <Link className="break-all font-mono text-xs text-cyan-300 hover:text-cyan-100" href={`/traces?traceId=${encodeURIComponent(traceId)}`}>
          {traceId}
        </Link>
      ) : (
        <div className="text-slate-400">Unavailable</div>
      )}
    </div>
  );
}
