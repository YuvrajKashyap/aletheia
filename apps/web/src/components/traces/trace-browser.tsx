"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { AppShell } from "@/components/layout/app-shell";
import { TraceDetail } from "@/components/traces/trace-detail";
import { TraceFilters, type TraceFiltersState } from "@/components/traces/trace-filters";
import { TraceList } from "@/components/traces/trace-list";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import { getTrace, getTraces } from "@/lib/api/traces";
import type { TraceDetailResponse, TraceListItem } from "@/lib/api/types";
import { API_BASE_URL } from "@/lib/config";

type ErrorState = {
  status?: number;
  message: string;
  body?: unknown;
};

const initialFilters: TraceFiltersState = {
  retrievalMode: "all",
  status: "all",
  limit: 25
};

function apiError(caught: unknown): ErrorState {
  if (caught instanceof ApiError) {
    return { status: caught.status, message: caught.message, body: caught.body };
  }
  if (caught instanceof TypeError) {
    return { message: `Backend API is not reachable at ${API_BASE_URL}.` };
  }
  return { message: caught instanceof Error ? caught.message : "Trace request failed." };
}

export function TraceBrowser() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTraceId = searchParams.get("traceId");
  const [filters, setFilters] = useState<TraceFiltersState>(initialFilters);
  const [traces, setTraces] = useState<TraceListItem[]>([]);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(initialTraceId);
  const [detail, setDetail] = useState<TraceDetailResponse | null>(null);
  const [listError, setListError] = useState<ErrorState | null>(null);
  const [detailError, setDetailError] = useState<ErrorState | null>(null);
  const [listLoading, setListLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [refreshCounter, setRefreshCounter] = useState(0);

  const loadTraces = useCallback(async () => {
    setListLoading(true);
    setListError(null);
    try {
      const response = await getTraces({
        retrievalMode: filters.retrievalMode,
        status: filters.status,
        limit: filters.limit,
        offset: 0
      });
      setTraces(response.items || []);
      if (!selectedTraceId && response.items?.[0]?.trace_id) {
        setSelectedTraceId(response.items[0].trace_id);
      }
    } catch (caught) {
      setTraces([]);
      setListError(apiError(caught));
    } finally {
      setListLoading(false);
    }
  }, [filters, selectedTraceId]);

  const loadDetail = useCallback(async (traceId: string) => {
    setDetailLoading(true);
    setDetailError(null);
    setDetail(null);
    try {
      setDetail(await getTrace(traceId));
    } catch (caught) {
      setDetailError(apiError(caught));
    } finally {
      setDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadTraces();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, [loadTraces, refreshCounter]);

  useEffect(() => {
    if (selectedTraceId) {
      const timeoutId = window.setTimeout(() => {
        void loadDetail(selectedTraceId);
      }, 0);

      return () => window.clearTimeout(timeoutId);
    }
  }, [loadDetail, selectedTraceId]);

  function selectTrace(traceId: string) {
    setSelectedTraceId(traceId);
    router.replace(`/traces?traceId=${encodeURIComponent(traceId)}`, { scroll: false });
  }

  const selectedTraceInList = useMemo(
    () => traces.some((trace) => trace.trace_id === selectedTraceId),
    [traces, selectedTraceId]
  );

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge tone="neutral">Query Traces</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">Search observability console</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Inspect real search traces, pipeline stages, candidate provenance, rerank movement, and raw trace JSON.
              Search history with full retrieval traces and ranking provenance.
            </p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-400">
            API base <span className="ml-2 font-mono text-slate-200">{API_BASE_URL}</span>
          </div>
        </div>

        <TraceFilters
          value={filters}
          isLoading={listLoading}
          onChange={(next) => {
            setFilters(next);
            setSelectedTraceId(null);
            setDetail(null);
            router.replace("/traces", { scroll: false });
          }}
          onRefresh={() => setRefreshCounter((current) => current + 1)}
        />

        <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
          <div className="space-y-3">
            <div className="text-sm text-slate-400">
              {listLoading ? "Loading traces" : `${traces.length} traces loaded`}
              {selectedTraceId && !selectedTraceInList ? " including deep-linked trace" : ""}
            </div>
            {listError ? <ErrorCard title="Trace list request failed" error={listError} /> : null}
            {listLoading ? <LoadingCard label="Loading recent traces" /> : null}
            {!listLoading && !listError ? (
              <TraceList traces={traces} selectedTraceId={selectedTraceId} onSelect={selectTrace} />
            ) : null}
          </div>

          <div className="space-y-4">
            {detailError ? <ErrorCard title="Trace detail request failed" error={detailError} /> : null}
            {detailLoading ? <LoadingCard label="Loading trace detail" /> : null}
            {!selectedTraceId && !detailLoading && !detailError ? <EmptyDetail /> : null}
            {detail && !detailLoading ? <TraceDetail trace={detail} /> : null}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function LoadingCard({ label }: { label: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
        <CardDescription>Reading real trace data from FastAPI.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="h-20 animate-pulse rounded-md bg-slate-900" />
          <div className="h-20 animate-pulse rounded-md bg-slate-900" />
          <div className="h-20 animate-pulse rounded-md bg-slate-900" />
        </div>
      </CardContent>
    </Card>
  );
}

function EmptyDetail() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Select a trace</CardTitle>
        <CardDescription>Choose a trace from the list or open a `/traces?traceId=` deep link.</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-400">No fake trace details are shown when no real trace is selected.</p>
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
