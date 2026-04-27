"use client";

import { ExperimentModeBadge } from "@/components/experiments/experiment-mode-badge";
import { formatDate, getRrfK } from "@/components/experiments/experiment-data";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ExperimentConfigItem } from "@/lib/api/types";

type ExperimentConfigDetailProps = {
  config: ExperimentConfigItem | null;
};

export function ExperimentConfigDetail({ config }: ExperimentConfigDetailProps) {
  if (!config) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Select an experiment config</CardTitle>
          <CardDescription>No config is selected.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-400">Config details are shown only for real configs returned by FastAPI.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <CardTitle>{config.name}</CardTitle>
          <ExperimentModeBadge mode={config.retrieval_mode} />
          {config.is_default ? <Badge tone="good">Default</Badge> : null}
        </div>
        <CardDescription className="font-mono">{config.id}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Detail label="Top K final" value={config.top_k_final} />
          <Detail label="BM25 candidate K" value={config.bm25_candidate_k} />
          <Detail label="Dense candidate K" value={config.dense_candidate_k} />
          <Detail label="Hybrid candidate K" value={config.hybrid_candidate_k} />
          <Detail label="Rerank top N" value={config.rerank_top_n} />
          <Detail label="Fusion method" value={config.fusion_method} />
          <Detail label="RRF K" value={getRrfK(config)} />
          <Detail label="Created" value={formatDate(config.created_at)} />
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <Detail label="Embedding model" value={config.embedding_model} />
          <Detail label="Reranker model" value={config.reranker_model} />
        </div>
        {config.config_json ? (
          <details className="rounded-md border border-slate-800 bg-slate-950/70 p-3">
            <summary className="cursor-pointer text-sm font-medium text-slate-200">Raw config JSON</summary>
            <pre className="mt-3 max-h-72 overflow-auto text-xs text-slate-300">
              {JSON.stringify(config.config_json, null, 2)}
            </pre>
          </details>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Detail({ label, value }: { label: string; value?: string | number | boolean | null }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950/70 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 break-words text-sm text-slate-200">
        {value === null || value === undefined || value === "" ? "Unavailable" : String(value)}
      </div>
    </div>
  );
}
