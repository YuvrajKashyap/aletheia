import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type StagePanelProps = {
  stages: Record<string, unknown> | undefined;
};

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : undefined;
}

function formatValue(value: unknown): string {
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

const stageFields: Record<string, string[]> = {
  bm25: ["enabled", "latency_ms", "candidate_count", "result_count", "index_name"],
  dense: [
    "enabled",
    "latency_ms",
    "embedding_latency_ms",
    "qdrant_latency_ms",
    "query_embedding_dimension",
    "candidate_count",
    "result_count",
    "collection_name"
  ],
  fusion: ["enabled", "latency_ms", "method", "rrf_k", "fused_candidate_count", "result_count"],
  reranker: ["enabled", "latency_ms", "model_name", "rerank_top_n", "scored_count", "result_count"]
};

export function TraceStagePanel({ stages }: StagePanelProps) {
  const entries = Object.entries(stages || {}).filter(([, value]) => asRecord(value));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pipeline stages</CardTitle>
      </CardHeader>
      <CardContent>
        {entries.length === 0 ? (
          <p className="text-sm text-slate-500">No stage data returned for this trace.</p>
        ) : (
          <div className="grid gap-3 xl:grid-cols-2">
            {entries.map(([name, value]) => {
              const stage = asRecord(value) || {};
              const keys = stageFields[name] || Object.keys(stage);
              return (
                <div className="rounded-lg border border-slate-800 bg-slate-950 p-3" key={name}>
                  <div className="mb-3 text-sm font-semibold capitalize text-slate-100">{name}</div>
                  <dl className="grid gap-2">
                    {keys
                      .filter((key) => stage[key] !== undefined)
                      .map((key) => (
                        <div className="flex items-center justify-between gap-4" key={key}>
                          <dt className="text-xs text-slate-500">{key}</dt>
                          <dd className="text-right font-mono text-xs text-slate-200">{formatValue(stage[key])}</dd>
                        </div>
                      ))}
                  </dl>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
