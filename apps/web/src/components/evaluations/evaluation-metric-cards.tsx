import { Card, CardContent } from "@/components/ui/card";
import type { EvaluationRunDetail, EvaluationRunItem } from "@/lib/api/types";
import { formatMetricValue } from "@/components/evaluations/metric-value";

type MetricCardsProps = {
  run: EvaluationRunDetail | EvaluationRunItem;
};

export function EvaluationMetricCards({ run }: MetricCardsProps) {
  const metrics = [
    { label: "Recall@5", value: run.recall_at_5, kind: "metric" as const },
    { label: "Recall@10", value: run.recall_at_10, kind: "metric" as const },
    { label: "MRR@10", value: run.mrr_at_10, kind: "metric" as const },
    { label: "NDCG@10", value: run.ndcg_at_10, kind: "metric" as const },
    { label: "Avg latency", value: run.avg_latency_ms, kind: "latency" as const },
    { label: "p50 latency", value: run.p50_latency_ms, kind: "latency" as const },
    { label: "p95 latency", value: run.p95_latency_ms, kind: "latency" as const },
    { label: "Failed queries", value: run.failed_query_count, kind: "count" as const }
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <Card key={metric.label}>
          <CardContent>
            <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{metric.label}</div>
            <div className="mt-2 font-mono text-xl font-semibold text-slate-100">
              {formatMetricValue(metric.value, metric.kind)}
            </div>
            {metric.label === "Failed queries" ? (
              <div className="mt-1 text-xs text-slate-500">of {run.query_count} total queries</div>
            ) : null}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
