"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { IndexAdminPanel } from "@/components/indexes/index-admin-panel";
import { IndexHealthCards } from "@/components/indexes/index-health-cards";
import { IndexJobTable } from "@/components/indexes/index-job-table";
import { IndexStatusCards } from "@/components/indexes/index-status-cards";
import { IndexVersionDetail } from "@/components/indexes/index-version-detail";
import { IndexVersionTable } from "@/components/indexes/index-version-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import {
  getIndexJobs,
  getIndexStatus,
  getIndexVersions,
  getOpenSearchHealth,
  getQdrantHealth
} from "@/lib/api/indexes";
import type {
  IndexJobItem,
  IndexStatusResponse,
  IndexVersionItem,
  OpenSearchHealthResponse,
  QdrantHealthResponse
} from "@/lib/api/types";
import { API_BASE_URL } from "@/lib/config";

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
  return { message: caught instanceof Error ? caught.message : "Index request failed." };
}

export function IndexConsole() {
  const [indexStatus, setIndexStatus] = useState<IndexStatusResponse | null>(null);
  const [versions, setVersions] = useState<IndexVersionItem[]>([]);
  const [jobs, setJobs] = useState<IndexJobItem[]>([]);
  const [openSearch, setOpenSearch] = useState<OpenSearchHealthResponse | null>(null);
  const [qdrant, setQdrant] = useState<QdrantHealthResponse | null>(null);
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [versionStatusFilter, setVersionStatusFilter] = useState("all");
  const [jobStatusFilter, setJobStatusFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);
  const [refreshCounter, setRefreshCounter] = useState(0);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [statusResponse, versionsResponse, jobsResponse, openSearchResponse, qdrantResponse] = await Promise.all([
        getIndexStatus(),
        getIndexVersions({ status: versionStatusFilter, limit: 50, offset: 0 }),
        getIndexJobs({ status: jobStatusFilter, limit: 50, offset: 0 }),
        getOpenSearchHealth(),
        getQdrantHealth()
      ]);

      setIndexStatus(statusResponse);
      setVersions(versionsResponse.items || []);
      setJobs(jobsResponse.items || []);
      setOpenSearch(openSearchResponse);
      setQdrant(qdrantResponse);
      setSelectedVersionId(
        (current) =>
          current ||
          statusResponse.active_index_version?.id ||
          versionsResponse.items?.find((version) => version.is_active)?.id ||
          versionsResponse.items?.[0]?.id ||
          null
      );
    } catch (caught) {
      setIndexStatus(null);
      setVersions([]);
      setJobs([]);
      setOpenSearch(null);
      setQdrant(null);
      setSelectedVersionId(null);
      setError(apiError(caught));
    } finally {
      setIsLoading(false);
    }
  }, [jobStatusFilter, versionStatusFilter]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadData();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadData, refreshCounter]);

  const selectedVersion = useMemo(
    () => versions.find((version) => version.id === selectedVersionId) || indexStatus?.active_index_version || null,
    [indexStatus?.active_index_version, selectedVersionId, versions]
  );

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge tone="neutral">Indexes</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">Index Console</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Inspect real active index metadata, index versions, OpenSearch and Qdrant health, and index build jobs.
            </p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-400">
            API base <span className="ml-2 font-mono text-slate-200">{API_BASE_URL}</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-4">
          <div className="text-sm text-slate-400">
            {error
              ? "No index data loaded."
              : isLoading
                ? "Loading index status, health, versions, and jobs."
                : `${versions.length} versions and ${jobs.length} jobs loaded from FastAPI.`}
          </div>
          <Button disabled={isLoading} type="button" onClick={() => setRefreshCounter((current) => current + 1)}>
            Refresh
          </Button>
        </div>

        {error ? <ErrorCard title="Index Console request failed" error={error} /> : null}

        <IndexStatusCards status={indexStatus} />
        <IndexHealthCards openSearch={openSearch} qdrant={qdrant} />

        <Card>
          <CardHeader>
            <CardTitle>Index versions</CardTitle>
            <CardDescription>Versioned metadata from FastAPI.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Filter label="Version status" value={versionStatusFilter} onChange={setVersionStatusFilter} />
            {isLoading ? <LoadingBlock /> : <IndexVersionTable versions={versions} selectedVersionId={selectedVersionId} onSelect={setSelectedVersionId} />}
          </CardContent>
        </Card>

        <IndexVersionDetail version={selectedVersion} />

        <Card>
          <CardHeader>
            <CardTitle>Index jobs</CardTitle>
            <CardDescription>Read-only history from the `index_jobs` table.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Filter label="Job status" value={jobStatusFilter} onChange={setJobStatusFilter} />
            {isLoading ? <LoadingBlock /> : <IndexJobTable jobs={jobs} />}
          </CardContent>
        </Card>

        <IndexAdminPanel selectedVersion={selectedVersion} onChanged={() => setRefreshCounter((current) => current + 1)} />
      </div>
    </AppShell>
  );
}

function Filter({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="grid max-w-xs gap-2">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <select
        className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="all">All statuses</option>
        <option value="pending">pending</option>
        <option value="building">building</option>
        <option value="ready">ready</option>
        <option value="active">active</option>
        <option value="completed">completed</option>
        <option value="failed">failed</option>
      </select>
    </label>
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
