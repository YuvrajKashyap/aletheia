"use client";

import { ModePill } from "@/components/search/mode-pill";
import { TraceStatusBadge } from "@/components/traces/trace-status-badge";
import type { TraceListItem } from "@/lib/api/types";

type TraceListProps = {
  traces: TraceListItem[];
  selectedTraceId: string | null;
  onSelect: (traceId: string) => void;
};

function shortId(value: string): string {
  return value.length > 10 ? value.slice(0, 8) : value;
}

function formatMs(value?: number | null): string {
  return value === null || value === undefined ? "latency unavailable" : `${value.toFixed(1)} ms`;
}

function formatDate(value?: string | null): string {
  if (!value) {
    return "time unavailable";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function TraceList({ traces, selectedTraceId, onSelect }: TraceListProps) {
  if (traces.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
        No traces returned for the current filters.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {traces.map((trace) => (
        <button
          className={`w-full rounded-lg border p-3 text-left transition focus:outline-none focus:ring-2 focus:ring-cyan-400/70 ${
            selectedTraceId === trace.trace_id
              ? "border-cyan-500 bg-cyan-950/30"
              : "border-slate-800 bg-slate-950/70 hover:border-slate-700"
          }`}
          key={trace.trace_id}
          type="button"
          onClick={() => onSelect(trace.trace_id)}
        >
          <div className="flex flex-wrap items-center gap-2">
            <ModePill mode={trace.retrieval_mode} />
            <TraceStatusBadge status={trace.status} />
            <span className="text-xs text-slate-500">{formatMs(trace.total_latency_ms)}</span>
          </div>
          <div className="mt-2 line-clamp-2 text-sm font-medium text-slate-100">{trace.query_text}</div>
          <div className="mt-3 grid gap-1 text-xs text-slate-500">
            <span>{formatDate(trace.created_at)}</span>
            <span className="font-mono">trace {shortId(trace.trace_id)}</span>
            <span className="font-mono">query {shortId(trace.query_id)}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
