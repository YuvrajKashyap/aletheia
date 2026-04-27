"use client";

import Link from "next/link";

import { formatMetricValue } from "@/components/evaluations/metric-value";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { EvaluationQueryResultItem } from "@/lib/api/types";

type QueryResultsTableProps = {
  results: EvaluationQueryResultItem[];
};

function preview(text: string): string {
  return text.length > 120 ? `${text.slice(0, 120)}...` : text;
}

export function EvaluationQueryResultsTable({ results }: QueryResultsTableProps) {
  if (results.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
        No query results returned for this run.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table className="min-w-[980px]">
        <TableHeader>
          <TableRow>
            <TableHead>Query ID</TableHead>
            <TableHead>Query</TableHead>
            <TableHead>Recall@10</TableHead>
            <TableHead>MRR@10</TableHead>
            <TableHead>NDCG@10</TableHead>
            <TableHead>Latency</TableHead>
            <TableHead>Error</TableHead>
            <TableHead>Trace</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {results.map((result) => (
            <TableRow key={result.id}>
              <TableCell className="font-mono">{result.query_external_id}</TableCell>
              <TableCell className="max-w-md text-slate-300">{preview(result.query_text)}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(result.recall_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(result.mrr_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(result.ndcg_at_10)}</TableCell>
              <TableCell className="font-mono">{formatMetricValue(result.latency_ms, "latency")}</TableCell>
              <TableCell className="max-w-xs text-red-200">{result.error_message || ""}</TableCell>
              <TableCell>
                {result.trace_id ? (
                  <Link
                    className="inline-flex h-8 items-center rounded-md border border-cyan-700 bg-cyan-950/60 px-3 text-xs font-semibold text-cyan-200 transition hover:border-cyan-400 hover:text-cyan-100 focus:outline-none focus:ring-2 focus:ring-cyan-400/70"
                    href={`/traces?traceId=${encodeURIComponent(result.trace_id)}`}
                  >
                    Open trace
                  </Link>
                ) : (
                  <span className="text-slate-500">Unavailable</span>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
