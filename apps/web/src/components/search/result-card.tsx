"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScoreBreakdown } from "@/components/search/score-breakdown";
import type { SearchResultItem } from "@/lib/api/types";

type ResultCardProps = {
  result: SearchResultItem;
};

function formatScore(score?: number | null): string {
  if (score === null || score === undefined) {
    return "score unavailable";
  }
  return score.toFixed(4);
}

function previewText(text: string, expanded: boolean): string {
  if (expanded || text.length <= 520) {
    return text;
  }
  return `${text.slice(0, 520).trim()}...`;
}

export function ResultCard({ result }: ResultCardProps) {
  const [expanded, setExpanded] = useState(false);
  const canExpand = result.text.length > 520;

  return (
    <Card>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="neutral">Rank {result.rank}</Badge>
              {result.document_external_id ? <Badge tone="neutral">{result.document_external_id}</Badge> : null}
              <span className="font-mono text-xs text-slate-400">{formatScore(result.score)}</span>
            </div>
            <h3 className="mt-3 text-base font-semibold text-slate-100">{result.title || "Untitled document chunk"}</h3>
          </div>
        </div>

        <div className="grid gap-2 text-xs md:grid-cols-2">
          <IdBlock label="chunk_id" value={result.chunk_id} />
          <IdBlock label="document_id" value={result.document_id} />
          {result.chunk_external_id ? <IdBlock label="chunk_external_id" value={result.chunk_external_id} /> : null}
          {result.dataset_id ? <IdBlock label="dataset_id" value={result.dataset_id} /> : null}
        </div>

        <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
          <p className="whitespace-pre-wrap text-sm leading-6 text-slate-300">{previewText(result.text, expanded)}</p>
          {canExpand ? (
            <button
              className="mt-3 text-sm font-medium text-cyan-300 hover:text-cyan-200"
              type="button"
              onClick={() => setExpanded((current) => !current)}
            >
              {expanded ? "Collapse text" : "Expand full text"}
            </button>
          ) : null}
        </div>

        <ScoreBreakdown scores={result.score_breakdown} />

        <div className="flex flex-wrap gap-2 text-xs text-slate-500">
          {result.token_count !== null && result.token_count !== undefined ? <span>{result.token_count} tokens</span> : null}
          {result.chunking_strategy ? <span>strategy {result.chunking_strategy}</span> : null}
          {result.chunking_version ? <span>version {result.chunking_version}</span> : null}
        </div>
      </CardContent>
    </Card>
  );
}

function IdBlock({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="min-w-0 rounded-md border border-slate-800 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 select-all truncate font-mono text-slate-300">{value || "unavailable"}</div>
    </div>
  );
}
