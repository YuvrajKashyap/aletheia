"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { EvaluationLatencyChart } from "@/components/evaluations/evaluation-latency-chart";
import { EvaluationMetricChart } from "@/components/evaluations/evaluation-metric-chart";
import { EvaluationRunDetailPanel } from "@/components/evaluations/evaluation-run-detail";
import { EvaluationRunTable } from "@/components/evaluations/evaluation-run-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import {
  getEvaluationRun,
  getEvaluationRunReport,
  getEvaluationRunResults,
  getEvaluationRuns
} from "@/lib/api/evaluations";
import type {
  EvaluationQueryResultItem,
  EvaluationReportResponse,
  EvaluationRunDetail,
  EvaluationRunItem
} from "@/lib/api/types";
import { API_BASE_URL } from "@/lib/config";

type ErrorState = {
  status?: number;
  message: string;
  body?: unknown;
};

type Filters = {
  status: string;
  limit: number;
};

function apiError(caught: unknown): ErrorState {
  if (caught instanceof ApiError) {
    return { status: caught.status, message: caught.message, body: caught.body };
  }
  if (caught instanceof TypeError) {
    return { message: `Backend API is not reachable at ${API_BASE_URL}.` };
  }
  return { message: caught instanceof Error ? caught.message : "Evaluation request failed." };
}

const initialFilters: Filters = {
  status: "all",
  limit: 25
};

export function EvaluationDashboard() {
  const [filters, setFilters] = useState<Filters>(initialFilters);
  const [runs, setRuns] = useState<EvaluationRunItem[]>([]);
  const [detailsByRunId, setDetailsByRunId] = useState<Record<string, EvaluationRunDetail>>({});
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [detail, setDetail] = useState<EvaluationRunDetail | null>(null);
  const [results, setResults] = useState<EvaluationQueryResultItem[]>([]);
  const [report, setReport] = useState<EvaluationReportResponse | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [listError, setListError] = useState<ErrorState | null>(null);
  const [detailError, setDetailError] = useState<ErrorState | null>(null);
  const [listLoading, setListLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [refreshCounter, setRefreshCounter] = useState(0);

  const loadRuns = useCallback(async () => {
    setListLoading(true);
    setListError(null);
    try {
      const response = await getEvaluationRuns({
        status: filters.status,
        limit: filters.limit,
        offset: 0
      });
      setRuns(response.items || []);
      setDetailsByRunId({});
      setSelectedRunId((current) => current || response.items?.[0]?.id || null);
    } catch (caught) {
      setRuns([]);
      setSelectedRunId(null);
      setListError(apiError(caught));
    } finally {
      setListLoading(false);
    }
  }, [filters]);

  const loadRunDetail = useCallback(async (runId: string) => {
    setDetailLoading(true);
    setDetailError(null);
    setReportError(null);
    setDetail(null);
    setResults([]);
    setReport(null);
    try {
      const [runDetail, runResults, runReport] = await Promise.allSettled([
        getEvaluationRun(runId),
        getEvaluationRunResults(runId, { limit: 50, offset: 0 }),
        getEvaluationRunReport(runId, { includeJson: true })
      ]);

      if (runDetail.status === "fulfilled") {
        setDetail(runDetail.value);
        setDetailsByRunId((current) => ({
          ...current,
          [runDetail.value.id]: runDetail.value
        }));
      } else {
        throw runDetail.reason;
      }

      if (runResults.status === "fulfilled") {
        setResults(runResults.value.items || []);
      }

      if (runReport.status === "fulfilled") {
        setReport(runReport.value);
      } else {
        const error = apiError(runReport.reason);
        setReportError(error.message);
      }
    } catch (caught) {
      setDetailError(apiError(caught));
    } finally {
      setDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadRuns();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadRuns, refreshCounter]);

  useEffect(() => {
    if (selectedRunId) {
      const timeoutId = window.setTimeout(() => {
        void loadRunDetail(selectedRunId);
      }, 0);
      return () => window.clearTimeout(timeoutId);
    }
  }, [loadRunDetail, selectedRunId]);

  const labeledRuns = useMemo(
    () =>
      runs.map((run) => {
        const runDetail = detailsByRunId[run.id];
        return runDetail ? { ...run, ...runDetail, config_json: runDetail.config_json } : run;
      }),
    [detailsByRunId, runs]
  );

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge tone="neutral">Evaluations</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">Evaluation observability dashboard</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Inspect real qrels-backed evaluation runs, aggregate metrics, per-query results, trace links, and stored
              report JSON.
            </p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-400">
            API base <span className="ml-2 font-mono text-slate-200">{API_BASE_URL}</span>
          </div>
        </div>

        <EvaluationFilters
          value={filters}
          isLoading={listLoading}
          onChange={(next) => {
            setFilters(next);
            setSelectedRunId(null);
            setDetail(null);
            setResults([]);
            setReport(null);
          }}
          onRefresh={() => setRefreshCounter((current) => current + 1)}
        />

        {listError ? <ErrorCard title="Evaluation run list failed" error={listError} /> : null}

        <div className="grid gap-4 xl:grid-cols-2">
          <EvaluationMetricChart runs={labeledRuns} />
          <EvaluationLatencyChart runs={labeledRuns} />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Evaluation runs</CardTitle>
            <CardDescription>
              {listError
                ? "No evaluation runs loaded."
                : listLoading
                  ? "Loading real evaluation runs."
                  : `${runs.length} runs loaded from FastAPI.`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {listLoading ? <LoadingBlock /> : <EvaluationRunTable runs={labeledRuns} selectedRunId={selectedRunId} onSelect={setSelectedRunId} />}
          </CardContent>
        </Card>

        {detailError ? <ErrorCard title="Evaluation run detail failed" error={detailError} /> : null}
        {detailLoading ? <LoadingCard label="Loading selected run" /> : null}
        {!selectedRunId && !detailLoading && !detailError ? <EmptyDetail /> : null}
        {detail && !detailLoading ? (
          <EvaluationRunDetailPanel run={detail} results={results} report={report} reportError={reportError} />
        ) : null}
      </div>
    </AppShell>
  );
}

function EvaluationFilters({
  value,
  isLoading,
  onChange,
  onRefresh
}: {
  value: Filters;
  isLoading: boolean;
  onChange: (value: Filters) => void;
  onRefresh: () => void;
}) {
  return (
    <div className="grid gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-4 md:grid-cols-[1fr_120px_auto]">
      <label className="grid gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Status</span>
        <select
          className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
          value={value.status}
          onChange={(event) => onChange({ ...value, status: event.target.value })}
        >
          <option value="all">All statuses</option>
          <option value="completed">completed</option>
          <option value="running">running</option>
          <option value="failed">failed</option>
        </select>
      </label>
      <label className="grid gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Limit</span>
        <select
          className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
          value={value.limit}
          onChange={(event) => onChange({ ...value, limit: Number(event.target.value) })}
        >
          <option value={25}>25</option>
          <option value={50}>50</option>
        </select>
      </label>
      <div className="flex items-end">
        <Button className="w-full" type="button" onClick={onRefresh} disabled={isLoading}>
          Refresh
        </Button>
      </div>
    </div>
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

function LoadingCard({ label }: { label: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
        <CardDescription>Reading real evaluation data from FastAPI.</CardDescription>
      </CardHeader>
      <CardContent>
        <LoadingBlock />
      </CardContent>
    </Card>
  );
}

function EmptyDetail() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Select an evaluation run</CardTitle>
        <CardDescription>No run is selected.</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-400">No fake run details are shown when no real run is selected.</p>
      </CardContent>
    </Card>
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
