"use client";

import type { FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { SearchMode, SearchRequest } from "@/lib/api/types";
import { getSearchModeLabel } from "@/lib/api/search";

export type SearchFormState = {
  query: string;
  retrievalMode: SearchMode;
  topK: number;
  candidateK: number;
  bm25CandidateK: number;
  denseCandidateK: number;
  hybridCandidateK: number;
  rerankTopN: number;
  rrfK: number;
  indexVersionId: string;
};

const modeDescriptions: Record<SearchMode, string> = {
  bm25: "Lexical search over the OpenSearch index.",
  dense: "Vector search using the embedding model and Qdrant.",
  hybrid: "BM25 plus dense search fused with Reciprocal Rank Fusion.",
  hybrid_rerank: "Hybrid candidates reranked by a cross-encoder."
};

const modes: SearchMode[] = ["bm25", "dense", "hybrid", "hybrid_rerank"];

type SearchFormProps = {
  state: SearchFormState;
  validationError: string | null;
  isLoading: boolean;
  isSnapshotMode?: boolean;
  onChange: (state: SearchFormState) => void;
  onSubmit: (request: SearchRequest) => void;
};

function numberValue(value: string): number {
  return Number.parseInt(value, 10) || 0;
}

export function buildSearchRequest(state: SearchFormState): SearchRequest {
  const base: SearchRequest = {
    query: state.query.trim(),
    retrieval_mode: state.retrievalMode,
    top_k: state.topK
  };

  const indexVersionId = state.indexVersionId.trim();
  if (indexVersionId) {
    base.index_version_id = indexVersionId;
  }

  if (state.retrievalMode === "bm25" || state.retrievalMode === "dense") {
    base.candidate_k = state.candidateK;
  }

  if (state.retrievalMode === "hybrid") {
    base.bm25_candidate_k = state.bm25CandidateK;
    base.dense_candidate_k = state.denseCandidateK;
    base.rrf_k = state.rrfK;
  }

  if (state.retrievalMode === "hybrid_rerank") {
    base.bm25_candidate_k = state.bm25CandidateK;
    base.dense_candidate_k = state.denseCandidateK;
    base.hybrid_candidate_k = state.hybridCandidateK;
    base.rerank_top_n = state.rerankTopN;
    base.rrf_k = state.rrfK;
  }

  return base;
}

export function validateSearchForm(state: SearchFormState): string | null {
  if (!state.query.trim()) {
    return "Query cannot be empty.";
  }
  if (state.topK < 1 || state.topK > 100) {
    return "top_k must be between 1 and 100.";
  }
  if ((state.retrievalMode === "bm25" || state.retrievalMode === "dense") && state.candidateK < state.topK) {
    return "candidate_k must be greater than or equal to top_k.";
  }
  if (state.retrievalMode === "hybrid" || state.retrievalMode === "hybrid_rerank") {
    if (state.bm25CandidateK < state.topK) {
      return "bm25_candidate_k must be greater than or equal to top_k.";
    }
    if (state.denseCandidateK < state.topK) {
      return "dense_candidate_k must be greater than or equal to top_k.";
    }
  }
  if (state.retrievalMode === "hybrid_rerank") {
    if (state.rerankTopN < state.topK) {
      return "rerank_top_n must be greater than or equal to top_k.";
    }
    if (state.hybridCandidateK < state.rerankTopN) {
      return "hybrid_candidate_k must be greater than or equal to rerank_top_n.";
    }
    if (state.bm25CandidateK < state.hybridCandidateK || state.denseCandidateK < state.hybridCandidateK) {
      return "BM25 and dense candidate counts must be greater than or equal to hybrid_candidate_k.";
    }
  }
  if (state.rrfK < 1) {
    return "rrf_k must be greater than 0.";
  }

  return null;
}

export function SearchForm({ state, validationError, isLoading, isSnapshotMode, onChange, onSubmit }: SearchFormProps) {
  function update(next: Partial<SearchFormState>) {
    onChange({ ...state, ...next });
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(buildSearchRequest(state));
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Search request</CardTitle>
        <CardDescription>
          {isSnapshotMode
            ? "Inspect real precomputed retrieval scenarios exported from the full local pipeline."
            : "Run real retrieval against FastAPI. This page does not generate answers."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-5" onSubmit={submit}>
          <label className="block">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Query</span>
            <textarea
              className="mt-2 min-h-28 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              placeholder={isSnapshotMode ? "Select a curated public demo query" : "Enter a SciFact-style retrieval query"}
              value={state.query}
              onChange={(event) => update({ query: event.target.value })}
            />
          </label>

          <div>
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Retrieval mode</span>
            <div className="mt-2 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
              {modes.map((mode) => (
                <button
                  className={`rounded-md border p-3 text-left transition focus:outline-none focus:ring-2 focus:ring-cyan-400/70 ${
                    state.retrievalMode === mode
                      ? "border-cyan-400 bg-cyan-950/40 text-cyan-100"
                      : "border-slate-800 bg-slate-950 text-slate-300 hover:border-slate-700"
                  }`}
                  key={mode}
                  type="button"
                  onClick={() => update({ retrievalMode: mode })}
                >
                  <span className="block text-sm font-semibold">{getSearchModeLabel(mode)}</span>
                  <span className="mt-1 block text-xs leading-5 text-slate-400">{modeDescriptions[mode]}</span>
                </button>
              ))}
            </div>
            {state.retrievalMode === "hybrid_rerank" ? (
              <p className="mt-2 text-xs text-amber-300">
                Hybrid rerank may take longer because it runs a cross-encoder.
              </p>
            ) : null}
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <NumberField label="top_k" max={100} min={1} value={state.topK} onChange={(topK) => update({ topK })} />
            {(state.retrievalMode === "bm25" || state.retrievalMode === "dense") && (
              <NumberField
                label="candidate_k"
                min={1}
                value={state.candidateK}
                onChange={(candidateK) => update({ candidateK })}
              />
            )}
            {(state.retrievalMode === "hybrid" || state.retrievalMode === "hybrid_rerank") && (
              <>
                <NumberField
                  label="bm25_candidate_k"
                  min={1}
                  value={state.bm25CandidateK}
                  onChange={(bm25CandidateK) => update({ bm25CandidateK })}
                />
                <NumberField
                  label="dense_candidate_k"
                  min={1}
                  value={state.denseCandidateK}
                  onChange={(denseCandidateK) => update({ denseCandidateK })}
                />
                <NumberField label="rrf_k" min={1} value={state.rrfK} onChange={(rrfK) => update({ rrfK })} />
              </>
            )}
            {state.retrievalMode === "hybrid_rerank" && (
              <>
                <NumberField
                  label="hybrid_candidate_k"
                  min={1}
                  value={state.hybridCandidateK}
                  onChange={(hybridCandidateK) => update({ hybridCandidateK })}
                />
                <NumberField
                  label="rerank_top_n"
                  min={1}
                  value={state.rerankTopN}
                  onChange={(rerankTopN) => update({ rerankTopN })}
                />
              </>
            )}
          </div>

          <label className="block">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Index version ID optional</span>
            <input
              className="mt-2 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-sm text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              placeholder="Use active index when blank"
              value={state.indexVersionId}
              onChange={(event) => update({ indexVersionId: event.target.value })}
            />
          </label>

          {validationError ? (
            <div className="rounded-md border border-red-900 bg-red-950/40 px-3 py-2 text-sm text-red-200">
              {validationError}
            </div>
          ) : null}

          <div className="flex justify-end">
            <Button type="submit" variant="primary" disabled={isLoading}>
              {isLoading ? "Running search" : isSnapshotMode ? "Load snapshot search" : "Run search"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

function NumberField({
  label,
  value,
  min,
  max,
  onChange
}: {
  label: string;
  value: number;
  min: number;
  max?: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <input
        className="mt-2 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-sm text-slate-100 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
        max={max}
        min={min}
        type="number"
        value={value}
        onChange={(event) => onChange(numberValue(event.target.value))}
      />
    </label>
  );
}
