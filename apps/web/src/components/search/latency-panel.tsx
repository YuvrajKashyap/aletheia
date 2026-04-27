import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SearchResponse } from "@/lib/api/types";

type LatencyPanelProps = {
  response: SearchResponse;
};

function formatMs(value?: number | null): string {
  if (value === null || value === undefined) {
    return "unavailable";
  }
  return `${value.toFixed(1)} ms`;
}

export function LatencyPanel({ response }: LatencyPanelProps) {
  const rows = [
    ["Total", response.latency_ms],
    ["BM25", response.bm25_latency_ms],
    ["Dense", response.dense_latency_ms],
    ["Embedding", response.embedding_latency_ms],
    ["Qdrant", response.qdrant_latency_ms],
    ["Fusion", response.fusion_latency_ms],
    ["Reranker", response.reranker_latency_ms]
  ].filter(([, value]) => value !== null && value !== undefined);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Latency</CardTitle>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <p className="text-sm text-slate-500">No latency fields returned.</p>
        ) : (
          <dl className="grid gap-2">
            {rows.map(([label, value]) => (
              <div className="flex items-center justify-between gap-4" key={label as string}>
                <dt className="text-sm text-slate-400">{label as string}</dt>
                <dd className="font-mono text-sm text-slate-100">{formatMs(value as number)}</dd>
              </div>
            ))}
          </dl>
        )}
      </CardContent>
    </Card>
  );
}
