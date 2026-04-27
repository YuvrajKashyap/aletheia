import Link from "next/link";
import type { ReactNode } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ModePill } from "@/components/search/mode-pill";
import type { SearchResponse } from "@/lib/api/types";

type MetadataPanelProps = {
  response: SearchResponse;
};

function valueOrUnknown(value?: string | number | null): string {
  if (value === null || value === undefined || value === "") {
    return "unavailable";
  }
  return String(value);
}

export function SearchMetadataPanel({ response }: MetadataPanelProps) {
  const parameters = [
    ["top_k", response.top_k],
    ["candidate_k", response.candidate_k],
    ["bm25_candidate_k", response.bm25_candidate_k],
    ["dense_candidate_k", response.dense_candidate_k],
    ["hybrid_candidate_k", response.hybrid_candidate_k],
    ["rerank_top_n", response.rerank_top_n],
    ["rrf_k", response.rrf_k]
  ].filter(([, value]) => value !== null && value !== undefined);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Search metadata</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <ModePill mode={response.retrieval_mode} />
          <span className="text-sm text-slate-400">{response.result_count} results returned</span>
        </div>
        <dl className="grid gap-3 text-sm">
          <MetadataRow label="query_id" value={response.query_id} />
          <MetadataRow
            label="trace_id"
            value={response.trace_id}
            action={
              <Link
                className="inline-flex h-8 items-center rounded-md border border-cyan-700 bg-cyan-950/60 px-3 text-xs font-semibold text-cyan-200 transition hover:border-cyan-400 hover:text-cyan-100 focus:outline-none focus:ring-2 focus:ring-cyan-400/70"
                href={`/traces?traceId=${encodeURIComponent(response.trace_id)}`}
              >
                Open trace
              </Link>
            }
          />
          <MetadataRow label="index_version_id" value={response.index_version_id} />
          <MetadataRow label="lexical index" value={response.lexical_index_name || response.index_name} />
          <MetadataRow label="vector collection" value={response.vector_collection_name || response.collection_name} />
        </dl>
        <div>
          <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">Request parameters</div>
          <div className="grid gap-2 sm:grid-cols-2">
            {parameters.map(([label, value]) => (
              <div className="flex items-center justify-between rounded-md border border-slate-800 px-3 py-2" key={label as string}>
                <span className="text-xs text-slate-500">{label as string}</span>
                <span className="font-mono text-sm text-slate-100">{valueOrUnknown(value as number)}</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function MetadataRow({
  label,
  value,
  action
}: {
  label: string;
  value?: string | null;
  action?: ReactNode;
}) {
  return (
    <div className="grid gap-1">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <span className="select-all break-all font-mono text-xs text-slate-200">{valueOrUnknown(value)}</span>
        {action}
      </dd>
    </div>
  );
}
