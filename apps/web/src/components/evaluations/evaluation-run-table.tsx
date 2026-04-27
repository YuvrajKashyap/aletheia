"use client";

import { EvaluationStatusBadge } from "@/components/evaluations/evaluation-status-badge";
import { formatMetricValue } from "@/components/evaluations/metric-value";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { EvaluationRunItem } from "@/lib/api/types";

type EvaluationRunTableProps = {
  runs: EvaluationRunItem[];
  selectedRunId: string | null;
  onSelect: (runId: string) => void;
};

function formatDate(value?: string | null): string {
  if (!value) {
    return "Unavailable";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function retrievalMode(run: EvaluationRunItem): string {
  const value = run.config_json?.retrieval_mode;
  return typeof value === "string" ? value : "Unknown mode";
}

export function EvaluationRunTable({ runs, selectedRunId, onSelect }: EvaluationRunTableProps) {
  if (runs.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
        No evaluation runs returned for the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table className="min-w-[980px]">
        <TableHeader>
          <TableRow>
            <TableHead>Run</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Mode</TableHead>
            <TableHead>Queries</TableHead>
            <TableHead>Failed</TableHead>
            <TableHead>Recall@10</TableHead>
            <TableHead>MRR@10</TableHead>
            <TableHead>NDCG@10</TableHead>
            <TableHead>Avg latency</TableHead>
            <TableHead>Report</TableHead>
            <TableHead>Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {runs.map((run) => (
            <TableRow
              className={`cursor-pointer transition hover:bg-slate-900/70 ${
                selectedRunId === run.id ? "bg-cyan-950/20" : ""
              }`}
              key={run.id}
              onClick={() => onSelect(run.id)}
            >
              <TableCell className="font-medium text-slate-100">{run.name}</TableCell>
              <TableCell>
                <EvaluationStatusBadge status={run.status} />
              </TableCell>
              <TableCell>{retrievalMode(run)}</TableCell>
              <TableCell className="font-mono">{run.query_count}</TableCell>
              <TableCell className="font-mono">{run.failed_query_count}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(run.recall_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(run.mrr_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(run.ndcg_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(run.avg_latency_ms, "latency")}</TableCell>
              <TableCell>{run.report_path ? "Available" : "Unavailable"}</TableCell>
              <TableCell>{formatDate(run.created_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
