import type { SearchMode, ReplaySavedQueryRequest } from "@/lib/api/types";
import { getSearchModeLabel } from "@/lib/api/search";

export type ReplayModeState = {
  retrievalMode: SearchMode;
  topK: number;
  candidateK: number;
  bm25CandidateK: number;
  denseCandidateK: number;
  hybridCandidateK: number;
  rerankTopN: number;
  rrfK: number;
  experimentConfigId: string;
  experimentConfigName: string;
};

const modes: SearchMode[] = ["bm25", "dense", "hybrid", "hybrid_rerank"];

export const defaultReplayModeState: ReplayModeState = {
  retrievalMode: "hybrid",
  topK: 10,
  candidateK: 10,
  bm25CandidateK: 50,
  denseCandidateK: 50,
  hybridCandidateK: 50,
  rerankTopN: 25,
  rrfK: 60,
  experimentConfigId: "",
  experimentConfigName: ""
};

function numberValue(value: string): number {
  return Number.parseInt(value, 10) || 0;
}

export function buildReplayRequest(
  state: ReplayModeState,
  extra: { sourceTraceId?: string; indexVersionId?: string } = {}
): ReplaySavedQueryRequest {
  const request: ReplaySavedQueryRequest = {
    retrieval_mode: state.retrievalMode,
    top_k: state.topK
  };

  if (state.experimentConfigId.trim()) {
    request.experiment_config_id = state.experimentConfigId.trim();
    delete request.retrieval_mode;
  } else if (state.experimentConfigName.trim()) {
    request.experiment_config_name = state.experimentConfigName.trim();
    delete request.retrieval_mode;
  }

  if (extra.sourceTraceId?.trim()) {
    request.source_trace_id = extra.sourceTraceId.trim();
  }
  if (extra.indexVersionId?.trim()) {
    request.index_version_id = extra.indexVersionId.trim();
  }

  if (state.retrievalMode === "bm25" || state.retrievalMode === "dense") {
    request.candidate_k = state.candidateK;
  }
  if (state.retrievalMode === "hybrid") {
    request.bm25_candidate_k = state.bm25CandidateK;
    request.dense_candidate_k = state.denseCandidateK;
    request.rrf_k = state.rrfK;
  }
  if (state.retrievalMode === "hybrid_rerank") {
    request.bm25_candidate_k = state.bm25CandidateK;
    request.dense_candidate_k = state.denseCandidateK;
    request.hybrid_candidate_k = state.hybridCandidateK;
    request.rerank_top_n = state.rerankTopN;
    request.rrf_k = state.rrfK;
  }

  return request;
}

export function validateReplayModeState(state: ReplayModeState): string | null {
  if (state.topK < 1 || state.topK > 100) return "top_k must be between 1 and 100.";
  if ((state.retrievalMode === "bm25" || state.retrievalMode === "dense") && state.candidateK < state.topK) {
    return "candidate_k must be greater than or equal to top_k.";
  }
  if (state.retrievalMode === "hybrid" || state.retrievalMode === "hybrid_rerank") {
    if (state.bm25CandidateK < state.topK) return "bm25_candidate_k must be greater than or equal to top_k.";
    if (state.denseCandidateK < state.topK) return "dense_candidate_k must be greater than or equal to top_k.";
  }
  if (state.retrievalMode === "hybrid_rerank") {
    if (state.rerankTopN < state.topK) return "rerank_top_n must be greater than or equal to top_k.";
    if (state.hybridCandidateK < state.rerankTopN) {
      return "hybrid_candidate_k must be greater than or equal to rerank_top_n.";
    }
  }
  if (state.rrfK < 1) return "rrf_k must be greater than 0.";
  return null;
}

export function ReplayModeControls({
  state,
  onChange
}: {
  state: ReplayModeState;
  onChange: (state: ReplayModeState) => void;
}) {
  function update(next: Partial<ReplayModeState>) {
    onChange({ ...state, ...next });
  }

  return (
    <div className="space-y-4">
      <div>
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Retrieval mode</span>
        <div className="mt-2 grid gap-2 sm:grid-cols-2">
          {modes.map((mode) => (
            <button
              className={`rounded-md border p-3 text-left text-sm transition focus:outline-none focus:ring-2 focus:ring-cyan-400/70 ${
                state.retrievalMode === mode
                  ? "border-cyan-400 bg-cyan-950/40 text-cyan-100"
                  : "border-slate-800 bg-slate-950 text-slate-300 hover:border-slate-700"
              }`}
              key={mode}
              type="button"
              onClick={() => update({ retrievalMode: mode })}
            >
              {getSearchModeLabel(mode)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <NumberField label="top_k" max={100} min={1} value={state.topK} onChange={(topK) => update({ topK })} />
        {(state.retrievalMode === "bm25" || state.retrievalMode === "dense") && (
          <NumberField label="candidate_k" min={1} value={state.candidateK} onChange={(candidateK) => update({ candidateK })} />
        )}
        {(state.retrievalMode === "hybrid" || state.retrievalMode === "hybrid_rerank") && (
          <>
            <NumberField label="bm25_candidate_k" min={1} value={state.bm25CandidateK} onChange={(bm25CandidateK) => update({ bm25CandidateK })} />
            <NumberField label="dense_candidate_k" min={1} value={state.denseCandidateK} onChange={(denseCandidateK) => update({ denseCandidateK })} />
            <NumberField label="rrf_k" min={1} value={state.rrfK} onChange={(rrfK) => update({ rrfK })} />
          </>
        )}
        {state.retrievalMode === "hybrid_rerank" && (
          <>
            <NumberField label="hybrid_candidate_k" min={1} value={state.hybridCandidateK} onChange={(hybridCandidateK) => update({ hybridCandidateK })} />
            <NumberField label="rerank_top_n" min={1} value={state.rerankTopN} onChange={(rerankTopN) => update({ rerankTopN })} />
          </>
        )}
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <TextField label="experiment_config_id optional" value={state.experimentConfigId} onChange={(experimentConfigId) => update({ experimentConfigId })} />
        <TextField label="experiment_config_name optional" value={state.experimentConfigName} onChange={(experimentConfigName) => update({ experimentConfigName })} />
      </div>
    </div>
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
        className="mt-2 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
        max={max}
        min={min}
        type="number"
        value={value}
        onChange={(event) => onChange(numberValue(event.target.value))}
      />
    </label>
  );
}

function TextField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <input
        className="mt-2 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}
