"use client";

import Link from "next/link";

import { BestMetricBadge } from "@/components/experiments/best-metric-badge";
import {
  formatCount,
  formatDate,
  formatLatency,
  formatMetric,
  type ExperimentMatrixRow
} from "@/components/experiments/experiment-data";
import { ExperimentModeBadge } from "@/components/experiments/experiment-mode-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type ExperimentMetricMatrixProps = {
  rows: ExperimentMatrixRow[];
};

export function ExperimentMetricMatrix({ rows }: ExperimentMetricMatrixProps) {
  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
        No experiment configs are available for comparison.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table className="min-w-[1180px]">
        <TableHeader>
          <TableRow>
            <TableHead>Config</TableHead>
            <TableHead>Mode</TableHead>
            <TableHead>Latest run</TableHead>
            <TableHead>Queries</TableHead>
            <TableHead>Failed</TableHead>
            <TableHead>Recall@10</TableHead>
            <TableHead>MRR@10</TableHead>
            <TableHead>NDCG@10</TableHead>
            <TableHead>Avg latency</TableHead>
            <TableHead>p50 latency</TableHead>
            <TableHead>p95 latency</TableHead>
            <TableHead>Badges</TableHead>
            <TableHead>Completed</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.config.id}>
              <TableCell>
                <div className="font-medium text-slate-100">{row.config.name}</div>
                <div className="mt-1 font-mono text-xs text-slate-500">{row.config.id}</div>
              </TableCell>
              <TableCell>
                <ExperimentModeBadge mode={row.config.retrieval_mode} />
              </TableCell>
              <TableCell>
                {row.latestRun ? (
                  <div className="space-y-2">
                    <Link className="font-medium text-cyan-300 underline-offset-4 hover:text-cyan-200 hover:underline" href="/evaluations">
                      {row.latestRun.name}
                    </Link>
                    <div>
                      <Link
                        className="inline-flex h-7 items-center rounded-md border border-cyan-800 bg-cyan-950/40 px-2 text-xs font-medium text-cyan-200 transition hover:border-cyan-500 hover:bg-cyan-900/50 hover:text-cyan-100 focus:outline-none focus:ring-2 focus:ring-cyan-400/70"
                        href="/evaluations"
                      >
                        Open evaluation
                      </Link>
                    </div>
                  </div>
                ) : (
                  <span className="text-slate-500">No evaluation run yet</span>
                )}
              </TableCell>
              <TableCell className="font-mono">{formatCount(row.latestRun?.query_count)}</TableCell>
              <TableCell className="font-mono">{formatCount(row.latestRun?.failed_query_count)}</TableCell>
              <TableCell className="font-mono">{formatMetric(row.latestRun?.recall_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetric(row.latestRun?.mrr_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetric(row.latestRun?.ndcg_at_10)}</TableCell>
              <TableCell className="font-mono">{formatLatency(row.latestRun?.avg_latency_ms)}</TableCell>
              <TableCell className="font-mono">{formatLatency(row.latestRun?.p50_latency_ms)}</TableCell>
              <TableCell className="font-mono">{formatLatency(row.latestRun?.p95_latency_ms)}</TableCell>
              <TableCell>
                {row.badges.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {row.badges.map((badge) => (
                      <BestMetricBadge key={badge} label={badge} />
                    ))}
                  </div>
                ) : (
                  <span className="text-slate-500">None</span>
                )}
              </TableCell>
              <TableCell>{formatDate(row.latestRun?.completed_at || row.latestRun?.created_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
