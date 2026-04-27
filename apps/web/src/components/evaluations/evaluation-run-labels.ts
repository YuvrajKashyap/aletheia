import type { EvaluationRunItem } from "@/lib/api/types";

const modeLabels: Record<string, string> = {
  bm25: "BM25",
  dense: "Dense",
  hybrid: "Hybrid RRF",
  hybrid_rerank: "Hybrid Rerank"
};

function stringField(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function shorten(value: string, maxLength = 22): string {
  return value.length > maxLength ? `${value.slice(0, maxLength - 3)}...` : value;
}

export function getEvaluationRunMode(run: EvaluationRunItem): string | null {
  return stringField(run.retrieval_mode) || stringField(run.config_json?.retrieval_mode);
}

export function getEvaluationRunModeLabel(run: EvaluationRunItem): string {
  const mode = getEvaluationRunMode(run);
  if (!mode) {
    return "Unknown mode";
  }
  return modeLabels[mode] || mode;
}

export function getEvaluationRunExperimentConfigName(run: EvaluationRunItem): string | null {
  return stringField(run.config_json?.experiment_config_name);
}

export function getEvaluationRunChartLabel(run: EvaluationRunItem): string {
  const configName = getEvaluationRunExperimentConfigName(run);
  if (configName) {
    return shorten(configName);
  }
  const mode = getEvaluationRunMode(run);
  if (mode) {
    return modeLabels[mode] || mode;
  }
  return shorten(run.name);
}
