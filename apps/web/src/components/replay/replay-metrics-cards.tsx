import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatMetricValue } from "@/components/evaluations/metric-value";

export function getNestedNumber(value: Record<string, unknown> | undefined, paths: string[]): number | null {
  for (const path of paths) {
    const result = path.split(".").reduce<unknown>((current, key) => {
      if (current && typeof current === "object" && key in current) {
        return (current as Record<string, unknown>)[key];
      }
      return undefined;
    }, value);
    if (typeof result === "number" && Number.isFinite(result)) {
      return result;
    }
  }
  return null;
}

export function ReplayMetricsCards({ comparison }: { comparison?: Record<string, unknown> }) {
  const metrics = [
    { label: "Recall@5", value: getNestedNumber(comparison, ["metrics.recall_at_5", "recall_at_5"]) },
    { label: "Recall@10", value: getNestedNumber(comparison, ["metrics.recall_at_10", "recall_at_10"]) },
    { label: "MRR@10", value: getNestedNumber(comparison, ["metrics.mrr_at_10", "mrr_at_10"]) },
    { label: "NDCG@10", value: getNestedNumber(comparison, ["metrics.ndcg_at_10", "ndcg_at_10"]) },
    { label: "Hit@5", value: getNestedNumber(comparison, ["metrics.hit_at_5", "hit_at_5"]) },
    { label: "Hit@10", value: getNestedNumber(comparison, ["metrics.hit_at_10", "hit_at_10"]) },
    { label: "Latency", value: getNestedNumber(comparison, ["metrics.latency_ms", "latency_ms"]), kind: "latency" as const }
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <Card key={metric.label}>
          <CardHeader>
            <CardTitle>{metric.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-white">
              {formatMetricValue(metric.value, metric.kind || "metric")}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
