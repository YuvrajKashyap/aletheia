"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { ModelStatusPanel } from "@/components/system/model-status-panel";
import { QueueStatusPanel } from "@/components/system/queue-status-panel";
import { SystemEventsTable } from "@/components/system/system-events-table";
import { SystemHealthGrid } from "@/components/system/system-health-grid";
import { SystemRefreshBar } from "@/components/system/system-refresh-bar";
import { WorkerHeartbeatPanel } from "@/components/system/worker-heartbeat-panel";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import {
  getApiHealth,
  getDbHealth,
  getEmbeddingModelStatus,
  getOpenSearchHealth,
  getQdrantHealth,
  getQueueStatus,
  getRerankerModelStatus,
  getSystemEvents,
  getWorkerHeartbeats
} from "@/lib/api/system";
import type {
  DbHealthResponse,
  HealthResponse,
  ModelStatusResponse,
  OpenSearchHealthResponse,
  QdrantHealthResponse,
  QueueStatusResponse,
  SystemEventItem,
  WorkerHeartbeatItem,
  WorkerHeartbeatListResponse
} from "@/lib/api/types";
import { API_BASE_URL } from "@/lib/config";
import { isSnapshotMode } from "@/lib/demo-mode";

type EndpointResult<T> = {
  data: T | null;
  error: string | null;
};

function emptyResult<T>(): EndpointResult<T> {
  return { data: null, error: null };
}

function errorMessage(error: unknown) {
  if (error instanceof ApiError) {
    return error.status ? `FastAPI returned status ${error.status}: ${error.message}` : error.message;
  }
  if (error instanceof TypeError) {
    return `Backend API is not reachable at ${API_BASE_URL}.`;
  }
  return error instanceof Error ? error.message : "Request failed.";
}

async function settle<T>(request: Promise<T>): Promise<EndpointResult<T>> {
  try {
    return { data: await request, error: null };
  } catch (error) {
    return { data: null, error: errorMessage(error) };
  }
}

function workerItems(response: WorkerHeartbeatListResponse | null): WorkerHeartbeatItem[] {
  return response?.items || response?.workers || response?.worker_heartbeats || [];
}

export function SystemHealthDashboard() {
  const snapshotMode = isSnapshotMode();
  const [api, setApi] = useState<EndpointResult<HealthResponse>>(emptyResult);
  const [db, setDb] = useState<EndpointResult<DbHealthResponse>>(emptyResult);
  const [queue, setQueue] = useState<EndpointResult<QueueStatusResponse>>(emptyResult);
  const [workers, setWorkers] = useState<EndpointResult<WorkerHeartbeatListResponse>>(emptyResult);
  const [openSearch, setOpenSearch] = useState<EndpointResult<OpenSearchHealthResponse>>(emptyResult);
  const [qdrant, setQdrant] = useState<EndpointResult<QdrantHealthResponse>>(emptyResult);
  const [embedding, setEmbedding] = useState<EndpointResult<ModelStatusResponse>>(emptyResult);
  const [reranker, setReranker] = useState<EndpointResult<ModelStatusResponse>>(emptyResult);
  const [events, setEvents] = useState<EndpointResult<{ total: number; items: SystemEventItem[] }>>(emptyResult);
  const [severity, setSeverity] = useState("all");
  const [eventType, setEventType] = useState("");
  const [limit, setLimit] = useState(50);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date | null>(null);
  const [refreshCounter, setRefreshCounter] = useState(0);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    const [
      apiResult,
      dbResult,
      queueResult,
      workersResult,
      openSearchResult,
      qdrantResult,
      embeddingResult,
      rerankerResult,
      eventsResult
    ] = await Promise.all([
      settle(getApiHealth()),
      settle(getDbHealth()),
      settle(getQueueStatus()),
      settle(getWorkerHeartbeats()),
      settle(getOpenSearchHealth()),
      settle(getQdrantHealth()),
      settle(getEmbeddingModelStatus()),
      settle(getRerankerModelStatus()),
      settle(getSystemEvents({ severity, eventType: eventType.trim() || undefined, limit, offset: 0 }))
    ]);

    setApi(apiResult);
    setDb(dbResult);
    setQueue(queueResult);
    setWorkers(workersResult);
    setOpenSearch(openSearchResult);
    setQdrant(qdrantResult);
    setEmbedding(embeddingResult);
    setReranker(rerankerResult);
    setEvents(
      eventsResult.data
        ? { data: { total: eventsResult.data.total, items: eventsResult.data.items || [] }, error: null }
        : { data: null, error: eventsResult.error }
    );
    setLastRefreshedAt(new Date());
    setIsLoading(false);
  }, [eventType, limit, severity]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadData();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadData, refreshCounter]);

  const workersList = useMemo(() => workerItems(workers.data), [workers.data]);
  const failedCount = [api, db, queue, workers, openSearch, qdrant, embedding, reranker, events].filter((result) => result.error).length;
  const coreOffline = Boolean(api.error && db.error && queue.error);

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge tone="neutral">Operations</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">System Health</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              {snapshotMode
                ? "Inspect public snapshot system state and exported events. Live backend services are disabled in hosted demo mode."
                : "Inspect API reachability, Postgres, Redis, workers, retrieval services, model status, and recent system events."}
            </p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-400">
            {snapshotMode ? "Snapshot source" : "API base"}{" "}
            <span className="ml-2 font-mono text-slate-200">
              {snapshotMode ? "/demo-data/system.json" : API_BASE_URL}
            </span>
          </div>
        </div>

        {snapshotMode ? (
          <Card className="border-cyan-900/60 bg-cyan-950/10">
            <CardHeader>
              <CardTitle>Public snapshot system state</CardTitle>
              <CardDescription>
                Hosted public mode serves the Vercel frontend and static snapshot data. FastAPI, Redis/RQ, OpenSearch,
                Qdrant, workers, embeddings, and reranking run in the full local stack.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : null}

        <SystemRefreshBar
          isLoading={isLoading}
          lastRefreshedAt={lastRefreshedAt}
          failedCount={failedCount}
          onRefresh={() => setRefreshCounter((current) => current + 1)}
        />

        {coreOffline ? (
          <Card className="border-red-900 bg-red-950/20">
            <CardHeader>
              <CardTitle>System Health request failed</CardTitle>
              <CardDescription>The backend request did not complete.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-red-200">Backend API is not reachable at {API_BASE_URL}.</p>
            </CardContent>
          </Card>
        ) : null}

        <SystemHealthGrid
          api={api}
          db={db}
          queue={queue}
          workers={{ data: workersList, error: workers.error }}
          openSearch={openSearch}
          qdrant={qdrant}
          embedding={embedding}
          reranker={reranker}
        />

        <div className="grid gap-4 xl:grid-cols-2">
          <QueueStatusPanel queue={queue.data} error={queue.error} />
          <ModelStatusPanel
            embedding={embedding.data}
            embeddingError={embedding.error}
            reranker={reranker.data}
            rerankerError={reranker.error}
          />
        </div>

        <WorkerHeartbeatPanel workers={workersList} error={workers.error} />

        <SystemEventsTable
          events={events.data?.items || []}
          total={events.data?.total}
          error={events.error}
          severity={severity}
          eventType={eventType}
          limit={limit}
          onSeverityChange={setSeverity}
          onEventTypeChange={setEventType}
          onLimitChange={setLimit}
        />
      </div>
    </AppShell>
  );
}
