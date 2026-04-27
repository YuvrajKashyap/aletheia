import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type ScoreBreakdownProps = {
  scores?: Record<string, number | string | null>;
};

const preferredLabels: Record<string, string> = {
  bm25_score: "BM25 score",
  dense_score: "Dense score",
  fusion_score: "Fusion score",
  reranker_score: "Reranker score",
  bm25_rank: "BM25 rank",
  dense_rank: "Dense rank",
  fusion_rank: "Fusion rank",
  rerank_rank: "Rerank rank"
};

function formatValue(value: number | string | null): string {
  if (value === null) {
    return "unavailable";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }
  return value;
}

function labelFor(key: string): string {
  return preferredLabels[key] || key.replaceAll("_", " ");
}

export function ScoreBreakdown({ scores }: ScoreBreakdownProps) {
  const entries = Object.entries(scores || {}).filter(([, value]) => value !== undefined);

  if (entries.length === 0) {
    return <p className="text-xs text-slate-500">No score breakdown returned.</p>;
  }

  return (
    <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
      {entries.map(([key, value]) => (
        <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2" key={key}>
          <div className="text-[11px] uppercase tracking-wide text-slate-500">{labelFor(key)}</div>
          <div className="mt-1 font-mono text-sm text-slate-100">{formatValue(value)}</div>
        </div>
      ))}
    </div>
  );
}

export function ScoreBreakdownCard({ scores }: ScoreBreakdownProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Score breakdown</CardTitle>
      </CardHeader>
      <CardContent>
        <ScoreBreakdown scores={scores} />
      </CardContent>
    </Card>
  );
}
