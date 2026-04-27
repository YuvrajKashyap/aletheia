"use client";

import { Button } from "@/components/ui/button";
import type { SearchMode } from "@/lib/api/types";

export type TraceFiltersState = {
  retrievalMode: SearchMode | "all";
  status: string;
  limit: number;
};

type TraceFiltersProps = {
  value: TraceFiltersState;
  isLoading: boolean;
  onChange: (value: TraceFiltersState) => void;
  onRefresh: () => void;
};

const retrievalModes: Array<SearchMode | "all"> = ["all", "bm25", "dense", "hybrid", "hybrid_rerank"];
const statuses = ["all", "completed", "failed", "running"];

function modeLabel(mode: SearchMode | "all"): string {
  const labels: Record<SearchMode | "all", string> = {
    all: "All modes",
    bm25: "BM25",
    dense: "Dense",
    hybrid: "Hybrid RRF",
    hybrid_rerank: "Hybrid Rerank"
  };
  return labels[mode];
}

export function TraceFilters({ value, isLoading, onChange, onRefresh }: TraceFiltersProps) {
  return (
    <div className="grid gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-4 md:grid-cols-[1fr_1fr_120px_auto]">
      <label className="grid gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Retrieval mode</span>
        <select
          className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
          value={value.retrievalMode}
          onChange={(event) => onChange({ ...value, retrievalMode: event.target.value as SearchMode | "all" })}
        >
          {retrievalModes.map((mode) => (
            <option key={mode} value={mode}>
              {modeLabel(mode)}
            </option>
          ))}
        </select>
      </label>
      <label className="grid gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Status</span>
        <select
          className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
          value={value.status}
          onChange={(event) => onChange({ ...value, status: event.target.value })}
        >
          {statuses.map((status) => (
            <option key={status} value={status}>
              {status === "all" ? "All statuses" : status}
            </option>
          ))}
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
