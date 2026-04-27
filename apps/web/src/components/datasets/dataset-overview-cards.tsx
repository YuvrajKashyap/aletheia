import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DatasetStatsResponse, DatasetSummary } from "@/lib/api/types";

function valueText(value?: number | string | null) {
  return value === null || value === undefined || value === "" ? "Unavailable" : String(value);
}

export function DatasetOverviewCards({
  dataset,
  stats
}: {
  dataset: DatasetSummary | null;
  stats: DatasetStatsResponse | null;
}) {
  const documentCount = stats?.document_count ?? dataset?.document_count ?? null;
  const chunkCount = stats?.chunk_count ?? dataset?.chunk_count ?? null;
  const queryCount = stats?.benchmark_query_count ?? dataset?.benchmark_query_count ?? null;
  const qrelCount = stats?.relevance_judgment_count ?? dataset?.relevance_judgment_count ?? null;
  const ratio =
    typeof documentCount === "number" && documentCount > 0 && typeof chunkCount === "number"
      ? (chunkCount / documentCount).toFixed(2)
      : null;

  const cards = [
    { label: "Dataset", value: dataset ? `${dataset.name} ${dataset.version}` : "Unavailable" },
    { label: "Documents", value: valueText(documentCount) },
    { label: "Chunks", value: valueText(chunkCount) },
    { label: "Benchmark queries", value: valueText(queryCount) },
    { label: "Qrels", value: valueText(qrelCount) },
    { label: "Chunks per document", value: ratio ?? "Unavailable" }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.label}>
          <CardHeader>
            <CardTitle>{card.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-white">{card.value}</div>
            {card.label === "Dataset" && dataset?.source ? (
              <p className="mt-2 text-sm text-slate-500">Source: {dataset.source}</p>
            ) : null}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
