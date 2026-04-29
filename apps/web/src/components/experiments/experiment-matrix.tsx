"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { ExperimentAdminPanel } from "@/components/experiments/experiment-admin-panel";
import { ExperimentConfigDetail } from "@/components/experiments/experiment-config-detail";
import { ExperimentConfigTable } from "@/components/experiments/experiment-config-table";
import {
  buildBestMetricBadges,
  formatLatency,
  formatMetric,
  getRunTimestamp,
  numericRunValue,
  type ExperimentMatrixRow
} from "@/components/experiments/experiment-data";
import { ExperimentLatencyChart } from "@/components/experiments/experiment-latency-chart";
import { ExperimentMetricMatrix } from "@/components/experiments/experiment-metric-matrix";
import { ExperimentQualityChart } from "@/components/experiments/experiment-quality-chart";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import { getEvaluationRuns } from "@/lib/api/evaluations";
import { getExperimentConfigs } from "@/lib/api/experiments";
import type { EvaluationRunItem, ExperimentConfigItem } from "@/lib/api/types";
import { API_BASE_URL } from "@/lib/config";
import { isSnapshotMode } from "@/lib/demo-mode";

type ErrorState = {
  status?: number;
  message: string;
  body?: unknown;
};

function apiError(caught: unknown): ErrorState {
  if (caught instanceof ApiError) {
    return { status: caught.status, message: caught.message, body: caught.body };
  }
  if (caught instanceof TypeError) {
    return { message: `Backend API is not reachable at ${API_BASE_URL}.` };
  }
  return { message: caught instanceof Error ? caught.message : "Experiment request failed." };
}

function runConfigId(run: EvaluationRunItem): string | null {
  if (run.experiment_config_id) {
    return run.experiment_config_id;
  }
  const value = run.config_json?.experiment_config_id;
  return typeof value === "string" && value.trim() ? value : null;
}

function latestCompletedRun(configId: string, runs: EvaluationRunItem[]): EvaluationRunItem | null {
  return (
    runs
      .filter((run) => run.status === "completed" && runConfigId(run) === configId)
      .sort((left, right) => getRunTimestamp(right) - getRunTimestamp(left))[0] || null
  );
}

export function ExperimentMatrix() {
  const snapshotMode = isSnapshotMode();
  const [configs, setConfigs] = useState<ExperimentConfigItem[]>([]);
  const [runs, setRuns] = useState<EvaluationRunItem[]>([]);
  const [selectedConfigId, setSelectedConfigId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);
  const [refreshCounter, setRefreshCounter] = useState(0);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [configResponse, runResponse] = await Promise.all([
        getExperimentConfigs({ limit: 100, offset: 0 }),
        getEvaluationRuns({ status: "all", limit: 100, offset: 0 })
      ]);
      setConfigs(configResponse.items || []);
      setRuns(runResponse.items || []);
      setSelectedConfigId((current) => current || configResponse.items?.[0]?.id || null);
    } catch (caught) {
      setConfigs([]);
      setRuns([]);
      setSelectedConfigId(null);
      setError(apiError(caught));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadData();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadData, refreshCounter]);

  const rows = useMemo<ExperimentMatrixRow[]>(() => {
    const rowsWithoutBadges = configs.map((config) => ({
      config,
      latestRun: latestCompletedRun(config.id, runs)
    }));
    const badgeMap = buildBestMetricBadges(rowsWithoutBadges);
    return rowsWithoutBadges.map((row) => ({
      ...row,
      badges: badgeMap[row.config.id] || []
    }));
  }, [configs, runs]);

  const selectedConfig = useMemo(
    () => configs.find((config) => config.id === selectedConfigId) || null,
    [configs, selectedConfigId]
  );

  const completedRunCount = rows.filter((row) => row.latestRun).length;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge tone="neutral">Experiments</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">Experiment comparison matrix</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              {snapshotMode
                ? "Compare exported retrieval configs against real qrels-backed evaluation runs from the full local pipeline."
                : "Compare real retrieval configs against their latest completed qrels-backed evaluation runs. Best-by-metric indicators are computed only from real numeric fields."}
            </p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-400">
            {snapshotMode ? "Snapshot source" : "API base"}{" "}
            <span className="ml-2 font-mono text-slate-200">
              {snapshotMode ? "/demo-data/experiments.json" : API_BASE_URL}
            </span>
          </div>
        </div>

        {snapshotMode ? (
          <Card className="border-cyan-900/60 bg-cyan-950/10">
            <CardHeader>
              <CardTitle>Public experiment snapshot</CardTitle>
              <CardDescription>
                Best-by-metric indicators use real exported evaluation metrics. Admin comparison jobs are disabled
                publicly.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : null}

        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-4">
          <div className="text-sm text-slate-400">
            {error
              ? "No experiment data loaded."
              : isLoading
                ? "Loading experiment configs and evaluation runs."
                : `${configs.length} configs and ${completedRunCount} latest completed runs loaded.`}
          </div>
          <Button disabled={isLoading} type="button" onClick={() => setRefreshCounter((current) => current + 1)}>
            Refresh
          </Button>
        </div>

        {error ? <ErrorCard title="Experiment matrix request failed" error={error} /> : null}

        <SummaryCards rows={rows} />

        <div className="grid gap-4 xl:grid-cols-2">
          <ExperimentQualityChart rows={rows} />
          <ExperimentLatencyChart rows={rows} />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Comparison matrix</CardTitle>
            <CardDescription>
              Latest completed evaluation run per experiment config. Missing values stay unavailable.
            </CardDescription>
          </CardHeader>
          <CardContent>{isLoading ? <LoadingBlock /> : <ExperimentMetricMatrix rows={rows} />}</CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Experiment configs</CardTitle>
            <CardDescription>Reusable retrieval parameter sets returned by FastAPI.</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingBlock />
            ) : (
              <ExperimentConfigTable
                configs={configs}
                selectedConfigId={selectedConfigId}
                onSelect={setSelectedConfigId}
              />
            )}
          </CardContent>
        </Card>

        <ExperimentConfigDetail config={selectedConfig} />
        <ExperimentAdminPanel onDataChanged={() => setRefreshCounter((current) => current + 1)} />
      </div>
    </AppShell>
  );
}

function SummaryCards({ rows }: { rows: ExperimentMatrixRow[] }) {
  const comparableRows = rows.filter((row) => row.latestRun);
  const bestRecall = bestRows(comparableRows, "recall_at_10", "high");
  const bestMrr = bestRows(comparableRows, "mrr_at_10", "high");
  const bestNdcg = bestRows(comparableRows, "ndcg_at_10", "high");
  const fastest = bestRows(comparableRows, "avg_latency_ms", "low");

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <BestCard label="Best Recall@10" rows={bestRecall} valueKind="metric" />
      <BestCard label="Best MRR@10" rows={bestMrr} valueKind="metric" />
      <BestCard label="Best NDCG@10" rows={bestNdcg} valueKind="metric" />
      <BestCard label="Fastest avg latency" rows={fastest} valueKind="latency" />
    </div>
  );
}

function bestRows(rows: ExperimentMatrixRow[], key: "recall_at_10" | "mrr_at_10" | "ndcg_at_10" | "avg_latency_ms", direction: "high" | "low") {
  const comparable = rows
    .map((row) => ({ row, value: numericRunValue(row.latestRun, key) }))
    .filter((item): item is { row: ExperimentMatrixRow; value: number } => item.value !== null);

  if (comparable.length < 2) {
    return [];
  }

  const bestValue =
    direction === "high"
      ? Math.max(...comparable.map((item) => item.value))
      : Math.min(...comparable.map((item) => item.value));

  return comparable.filter((item) => item.value === bestValue);
}

function BestCard({
  label,
  rows,
  valueKind
}: {
  label: string;
  rows: Array<{ row: ExperimentMatrixRow; value: number }>;
  valueKind: "metric" | "latency";
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">{label}</CardTitle>
        <CardDescription>Computed from latest completed runs.</CardDescription>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <p className="text-sm text-slate-500">Not enough comparable data.</p>
        ) : (
          <div className="space-y-2">
            {rows.map((item) => (
              <div key={item.row.config.id}>
                <div className="text-sm font-medium text-slate-100">{item.row.config.name}</div>
                <div className="font-mono text-sm text-cyan-200">
                  {valueKind === "latency" ? formatLatency(item.value) : formatMetric(item.value)}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function LoadingBlock() {
  return (
    <div className="space-y-3">
      <div className="h-14 animate-pulse rounded-md bg-slate-900" />
      <div className="h-14 animate-pulse rounded-md bg-slate-900" />
      <div className="h-14 animate-pulse rounded-md bg-slate-900" />
    </div>
  );
}

function ErrorCard({ title, error }: { title: string; error: ErrorState }) {
  return (
    <Card className="border-red-900 bg-red-950/20">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>
          {error.status ? `FastAPI returned status ${error.status}.` : "The backend request did not complete."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-red-200">{error.message}</p>
        {error.body !== undefined ? (
          <pre className="max-h-72 overflow-auto rounded-md border border-red-900 bg-slate-950 p-3 text-xs text-slate-300">
            {typeof error.body === "string" ? error.body : JSON.stringify(error.body, null, 2)}
          </pre>
        ) : null}
      </CardContent>
    </Card>
  );
}
