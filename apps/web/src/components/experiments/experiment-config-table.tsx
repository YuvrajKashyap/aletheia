"use client";

import { ExperimentModeBadge } from "@/components/experiments/experiment-mode-badge";
import { formatDate, getRrfK } from "@/components/experiments/experiment-data";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { ExperimentConfigItem } from "@/lib/api/types";

type ExperimentConfigTableProps = {
  configs: ExperimentConfigItem[];
  selectedConfigId: string | null;
  onSelect: (configId: string) => void;
};

export function ExperimentConfigTable({ configs, selectedConfigId, onSelect }: ExperimentConfigTableProps) {
  if (configs.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
        No experiment configs returned by FastAPI.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table className="min-w-[980px]">
        <TableHeader>
          <TableRow>
            <TableHead>Config</TableHead>
            <TableHead>Mode</TableHead>
            <TableHead>Top K</TableHead>
            <TableHead>BM25 K</TableHead>
            <TableHead>Dense K</TableHead>
            <TableHead>Hybrid K</TableHead>
            <TableHead>Rerank N</TableHead>
            <TableHead>Fusion</TableHead>
            <TableHead>RRF K</TableHead>
            <TableHead>Default</TableHead>
            <TableHead>Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {configs.map((config) => (
            <TableRow
              className={`cursor-pointer transition hover:bg-slate-900/70 ${
                selectedConfigId === config.id ? "bg-cyan-950/20" : ""
              }`}
              key={config.id}
              onClick={() => onSelect(config.id)}
            >
              <TableCell>
                <div className="font-medium text-slate-100">{config.name}</div>
                <div className="mt-1 font-mono text-xs text-slate-500">{config.id}</div>
              </TableCell>
              <TableCell>
                <ExperimentModeBadge mode={config.retrieval_mode} />
              </TableCell>
              <TableCell className="font-mono">{config.top_k_final ?? "Unavailable"}</TableCell>
              <TableCell className="font-mono">{config.bm25_candidate_k ?? "Unavailable"}</TableCell>
              <TableCell className="font-mono">{config.dense_candidate_k ?? "Unavailable"}</TableCell>
              <TableCell className="font-mono">{config.hybrid_candidate_k ?? "Unavailable"}</TableCell>
              <TableCell className="font-mono">{config.rerank_top_n ?? "Unavailable"}</TableCell>
              <TableCell>{config.fusion_method || "Unavailable"}</TableCell>
              <TableCell className="font-mono">{getRrfK(config)}</TableCell>
              <TableCell>{config.is_default ? <Badge tone="good">Default</Badge> : "No"}</TableCell>
              <TableCell>{formatDate(config.created_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
