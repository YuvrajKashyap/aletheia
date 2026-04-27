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

function normalize(value: string): string {
  return value.toLowerCase().replaceAll("-", "_");
}

function deriveModeFromRunName(name: string): string | null {
  const normalized = normalize(name);
  if (normalized.includes("hybrid_rerank") || normalized.includes("hybrid rerank")) {
    return "hybrid_rerank";
  }
  if (normalized.includes("hybrid_rrf") || normalized.includes("hybrid limited") || normalized.includes("hybrid")) {
    return "hybrid";
  }
  if (normalized.includes("dense")) {
    return "dense";
  }
  if (normalized.includes("bm25")) {
    return "bm25";
  }
  return null;
}

function deriveConfigNameFromRunName(name: string): string | null {
  const normalized = normalize(name);
  for (const configName of ["hybrid_rerank_default", "hybrid_rrf_default", "dense_baseline", "bm25_baseline"]) {
    if (normalized.includes(configName)) {
      return configName;
    }
  }
  return null;
}

export function getEvaluationRunMode(run: EvaluationRunItem): string | null {
  return (
    stringField(run.retrieval_mode) ||
    stringField(run.config_json?.retrieval_mode) ||
    deriveModeFromRunName(run.name)
  );
}

export function getEvaluationRunModeLabel(run: EvaluationRunItem): string {
  const mode = getEvaluationRunMode(run);
  if (!mode) {
    return "Unknown mode";
  }
  return modeLabels[mode] || mode;
}

export function getEvaluationRunExperimentConfigName(run: EvaluationRunItem): string | null {
  return (
    stringField(run.config_json?.experiment_config_name) ||
    stringField(run.experiment_config_name) ||
    deriveConfigNameFromRunName(run.name)
  );
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
