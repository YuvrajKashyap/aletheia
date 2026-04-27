import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MetadataJsonPanel } from "@/components/datasets/metadata-json-panel";
import { RelevanceJudgmentTable } from "@/components/datasets/relevance-judgment-table";
import type { BenchmarkQueryDetailResponse, RelevanceJudgmentItem } from "@/lib/api/types";

export function BenchmarkQueryDetailPanel({
  query,
  judgments,
  loading,
  error
}: {
  query: BenchmarkQueryDetailResponse | null;
  judgments: RelevanceJudgmentItem[];
  loading?: boolean;
  error?: string | null;
}) {
  if (loading) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading benchmark query detail...</p>;
  }

  if (error) {
    return <p className="rounded-lg border border-red-900/70 p-4 text-sm text-red-300">{error}</p>;
  }

  if (!query) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Select a benchmark query to inspect qrels.</p>;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Benchmark Query {query.external_id}</CardTitle>
          <CardDescription>
            Split {query.split || "unknown"} · {query.relevance_judgment_count ?? "Unavailable"} qrels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="rounded-md border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-200">
            {query.text}
          </p>
          <div className="grid gap-3 text-sm md:grid-cols-2">
            <div>
              <div className="text-slate-500">Query ID</div>
              <div className="font-mono text-xs text-slate-300">{query.id}</div>
            </div>
            <div>
              <div className="text-slate-500">Dataset ID</div>
              <div className="font-mono text-xs text-slate-300">{query.dataset_id}</div>
            </div>
          </div>
        </CardContent>
      </Card>
      <MetadataJsonPanel value={query.metadata_json} />
      <Card>
        <CardHeader>
          <CardTitle>Query Relevance Judgments</CardTitle>
          <CardDescription>Real qrels linked to this benchmark query</CardDescription>
        </CardHeader>
        <CardContent>
          <RelevanceJudgmentTable judgments={judgments} />
        </CardContent>
      </Card>
    </div>
  );
}
