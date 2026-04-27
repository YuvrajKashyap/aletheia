import type { EvaluationRunItem, ExperimentConfigItem, SearchMode } from "@/lib/api/types";

export type BestMetricKey = "recall_at_10" | "mrr_at_10" | "ndcg_at_10" | "avg_latency_ms";

export type ExperimentMatrixRow = {
  config: ExperimentConfigItem;
  latestRun: EvaluationRunItem | null;
  badges: string[];
};

export const modeLabels: Record<SearchMode, string> = {
  bm25: "BM25",
  dense: "Dense",
  hybrid: "Hybrid RRF",
  hybrid_rerank: "Hybrid Rerank"
};

export function formatMetric(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(4) : "Unavailable";
}

export function formatLatency(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(1)} ms` : "Unavailable";
}

export function formatCount(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? String(value) : "Unavailable";
}

export function formatDate(value?: string | null): string {
  if (!value) {
    return "Unavailable";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function getModeLabel(mode?: string | null): string {
  if (mode === "bm25" || mode === "dense" || mode === "hybrid" || mode === "hybrid_rerank") {
    return modeLabels[mode];
  }
  return mode || "Unknown mode";
}

export function getRrfK(config: ExperimentConfigItem): string {
  const value = config.fusion_params_json?.rrf_k;
  return typeof value === "number" || typeof value === "string" ? String(value) : "Unavailable";
}

export function getRunTimestamp(run: EvaluationRunItem): number {
  const value = run.completed_at || run.created_at || run.started_at;
  if (!value) {
    return 0;
  }
  const time = new Date(value).getTime();
  return Number.isNaN(time) ? 0 : time;
}

export function numericRunValue(run: EvaluationRunItem | null, key: BestMetricKey): number | null {
  if (!run) {
    return null;
  }
  const value = run[key];
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function buildBestMetricBadges(rows: Omit<ExperimentMatrixRow, "badges">[]): Record<string, string[]> {
  const badgeMap: Record<string, string[]> = {};
  const definitions: Array<{ key: BestMetricKey; label: string; direction: "high" | "low" }> = [
    { key: "recall_at_10", label: "Best Recall@10", direction: "high" },
    { key: "mrr_at_10", label: "Best MRR@10", direction: "high" },
    { key: "ndcg_at_10", label: "Best NDCG@10", direction: "high" },
    { key: "avg_latency_ms", label: "Fastest", direction: "low" }
  ];

  for (const definition of definitions) {
    const comparable = rows
      .map((row) => ({ id: row.config.id, value: numericRunValue(row.latestRun, definition.key) }))
      .filter((row): row is { id: string; value: number } => row.value !== null);

    if (comparable.length < 2) {
      continue;
    }

    const bestValue =
      definition.direction === "high"
        ? Math.max(...comparable.map((row) => row.value))
        : Math.min(...comparable.map((row) => row.value));

    for (const row of comparable) {
      if (row.value === bestValue) {
        badgeMap[row.id] = [...(badgeMap[row.id] || []), definition.label];
      }
    }
  }

  return badgeMap;
}
