"use client";

import { useCallback, useEffect, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { QueryReplayDetailPanel } from "@/components/replay/query-replay-detail";
import { QueryReplayTable } from "@/components/replay/query-replay-table";
import { ReplayAdminPanel } from "@/components/replay/replay-admin-panel";
import { ReplayJobStatus } from "@/components/replay/replay-job-status";
import { SavedQueryDetailPanel } from "@/components/replay/saved-query-detail";
import { SavedQueryTable } from "@/components/replay/saved-query-table";
import {
  getJobStatus,
  getQueryReplay,
  getQueryReplays,
  getSavedQuery,
  getSavedQueries
} from "@/lib/api/replay";
import { API_BASE_URL } from "@/lib/config";
import type {
  JobStatusResponse,
  QueryReplayDetail,
  QueryReplayItem,
  ReplayResponse,
  SavedQueryDetail,
  SavedQueryItem
} from "@/lib/api/types";
import { isSnapshotMode } from "@/lib/demo-mode";

function errorMessage(error: unknown) {
  if (error instanceof TypeError && error.message.toLowerCase().includes("fetch")) {
    return `Backend API is not reachable at ${API_BASE_URL}.`;
  }
  if (error instanceof Error && error.message.toLowerCase() === "failed to fetch") {
    return `Backend API is not reachable at ${API_BASE_URL}.`;
  }
  return error instanceof Error ? error.message : "Request failed";
}

export function ReplayLab() {
  const snapshotMode = isSnapshotMode();
  const [sourceFilter, setSourceFilter] = useState("golden_scifact");
  const [statusFilter, setStatusFilter] = useState("all");
  const [savedLimit, setSavedLimit] = useState(25);
  const [replayLimit, setReplayLimit] = useState(25);
  const [savedQueries, setSavedQueries] = useState<SavedQueryItem[]>([]);
  const [queryReplays, setQueryReplays] = useState<QueryReplayItem[]>([]);
  const [savedError, setSavedError] = useState<string | null>(null);
  const [replayError, setReplayError] = useState<string | null>(null);
  const [isLoadingSaved, setIsLoadingSaved] = useState(false);
  const [isLoadingReplays, setIsLoadingReplays] = useState(false);
  const [selectedQuery, setSelectedQuery] = useState<SavedQueryDetail | null>(null);
  const [selectedReplay, setSelectedReplay] = useState<QueryReplayDetail | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [startedJob, setStartedJob] = useState<ReplayResponse | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [jobError, setJobError] = useState<string | null>(null);
  const [isJobLoading, setIsJobLoading] = useState(false);

  const loadSavedQueries = useCallback(async () => {
    setIsLoadingSaved(true);
    setSavedError(null);
    try {
      const response = await getSavedQueries({ source: sourceFilter, limit: savedLimit, offset: 0 });
      setSavedQueries(response.items);
      if (!selectedQuery && response.items[0]) {
        void selectSavedQuery(response.items[0]);
      }
    } catch (error) {
      setSavedError(errorMessage(error));
      setSavedQueries([]);
    } finally {
      setIsLoadingSaved(false);
    }
  }, [sourceFilter, savedLimit, selectedQuery]);

  const loadQueryReplays = useCallback(async () => {
    setIsLoadingReplays(true);
    setReplayError(null);
    try {
      const response = await getQueryReplays({ status: statusFilter, limit: replayLimit, offset: 0 });
      setQueryReplays(response.items);
    } catch (error) {
      setReplayError(errorMessage(error));
      setQueryReplays([]);
    } finally {
      setIsLoadingReplays(false);
    }
  }, [statusFilter, replayLimit]);

  async function selectSavedQuery(query: SavedQueryItem) {
    setDetailError(null);
    try {
      setSelectedQuery(await getSavedQuery(query.id));
    } catch (error) {
      setDetailError(errorMessage(error));
      setSelectedQuery(query);
    }
  }

  async function selectReplay(replay: QueryReplayItem) {
    setDetailError(null);
    try {
      setSelectedReplay(await getQueryReplay(replay.id));
    } catch (error) {
      setDetailError(errorMessage(error));
      setSelectedReplay(replay);
    }
  }

  async function refreshJob() {
    if (!startedJob?.job_id) return;
    setIsJobLoading(true);
    setJobError(null);
    try {
      const status = await getJobStatus(startedJob.job_id);
      setJobStatus(status);
      if (status.status === "finished") {
        void loadQueryReplays();
      }
    } catch (error) {
      setJobError(errorMessage(error));
    } finally {
      setIsJobLoading(false);
    }
  }

  function refreshAll() {
    void loadSavedQueries();
    void loadQueryReplays();
  }

  useEffect(() => {
    const timer = window.setTimeout(() => void loadSavedQueries(), 0);
    return () => window.clearTimeout(timer);
  }, [loadSavedQueries]);

  useEffect(() => {
    const timer = window.setTimeout(() => void loadQueryReplays(), 0);
    return () => window.clearTimeout(timer);
  }, [loadQueryReplays]);

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="space-y-3">
          <Badge tone="neutral">Replay Lab</Badge>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">Replay Lab</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                {snapshotMode
                  ? "Inspect real replay outputs exported from the full local stack, including metrics, document matches, and trace links."
                  : "Replay saved and golden queries through real retrieval paths, inspect metrics, and open generated traces."}
              </p>
              <div className="mt-2 font-mono text-xs text-slate-500">
                {snapshotMode ? "Snapshot source: /demo-data/replay.json" : `Backend: ${API_BASE_URL}`}
              </div>
            </div>
            <Button onClick={refreshAll}>Refresh</Button>
          </div>
        </section>

        {snapshotMode ? (
          <Card className="border-cyan-900/60 bg-cyan-950/10">
            <CardHeader>
              <CardTitle>Public replay snapshot</CardTitle>
              <CardDescription>
                Replay actions are disabled in public snapshot mode. The rows below are real replay outputs exported
                from the full local stack.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : null}

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_460px]">
          <section className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Saved queries</CardTitle>
                <CardDescription>
                  {snapshotMode ? "Golden and manual saved queries from snapshot exports." : "Golden and manual saved queries from FastAPI."}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap items-center gap-3">
                  <label className="text-xs text-slate-500">
                    Source
                    <select
                      className="ml-2 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-100"
                      value={sourceFilter}
                      onChange={(event) => {
                        setSelectedQuery(null);
                        setSourceFilter(event.target.value);
                      }}
                    >
                      <option value="golden_scifact">golden_scifact</option>
                      <option value="manual">manual</option>
                      <option value="all">all</option>
                    </select>
                  </label>
                  <label className="text-xs text-slate-500">
                    Limit
                    <select
                      className="ml-2 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-100"
                      value={savedLimit}
                      onChange={(event) => setSavedLimit(Number(event.target.value))}
                    >
                      {[10, 25, 50, 100].map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </label>
                </div>
                {savedError ? <p className="rounded-md border border-red-900/70 p-3 text-sm text-red-300">{savedError}</p> : null}
                {isLoadingSaved ? (
                  <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading saved queries...</p>
                ) : (
                  <SavedQueryTable queries={savedQueries} selectedQueryId={selectedQuery?.id} onSelect={selectSavedQuery} />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Query replays</CardTitle>
                <CardDescription>Persisted replay runs and trace links.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap items-center gap-3">
                  <label className="text-xs text-slate-500">
                    Status
                    <select
                      className="ml-2 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-100"
                      value={statusFilter}
                      onChange={(event) => setStatusFilter(event.target.value)}
                    >
                      <option value="all">all</option>
                      <option value="completed">completed</option>
                      <option value="failed">failed</option>
                      <option value="running">running</option>
                    </select>
                  </label>
                  <label className="text-xs text-slate-500">
                    Limit
                    <select
                      className="ml-2 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-100"
                      value={replayLimit}
                      onChange={(event) => setReplayLimit(Number(event.target.value))}
                    >
                      {[10, 25, 50, 100].map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </label>
                </div>
                {replayError ? <p className="rounded-md border border-red-900/70 p-3 text-sm text-red-300">{replayError}</p> : null}
                {isLoadingReplays ? (
                  <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading query replays...</p>
                ) : (
                  <QueryReplayTable replays={queryReplays} selectedReplayId={selectedReplay?.id} onSelect={selectReplay} />
                )}
              </CardContent>
            </Card>
          </section>

          <aside className="space-y-4 xl:sticky xl:top-6 xl:self-start">
            {detailError ? <p className="rounded-md border border-red-900/70 p-3 text-sm text-red-300">{detailError}</p> : null}
            <QueryReplayDetailPanel replay={selectedReplay} />
            <SavedQueryDetailPanel query={selectedQuery} />
          </aside>
        </div>

        <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
          <ReplayAdminPanel
            selectedQuery={selectedQuery}
            onActionComplete={refreshAll}
            onJobStarted={(response) => {
              setStartedJob(response);
              setJobStatus(null);
            }}
          />
          <ReplayJobStatus
            response={startedJob}
            jobStatus={jobStatus}
            isLoading={isJobLoading}
            error={jobError}
            onRefresh={refreshJob}
          />
        </section>
      </div>
    </AppShell>
  );
}
