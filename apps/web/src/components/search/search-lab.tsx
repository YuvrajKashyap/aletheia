"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { LatencyPanel } from "@/components/search/latency-panel";
import { SearchForm, buildSearchRequest, type SearchFormState, validateSearchForm } from "@/components/search/search-form";
import { SearchMetadataPanel } from "@/components/search/search-metadata-panel";
import { SearchResults } from "@/components/search/search-results";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import { getSearchModeLabel, runSearch } from "@/lib/api/search";
import { getSnapshotSearchScenarios } from "@/lib/api/snapshot";
import type { SearchMode, SearchRequest, SearchResponse } from "@/lib/api/types";
import { API_BASE_URL } from "@/lib/config";
import { isSnapshotMode } from "@/lib/demo-mode";

const initialState: SearchFormState = {
  query: "",
  retrievalMode: "bm25",
  topK: 5,
  candidateK: 10,
  bm25CandidateK: 50,
  denseCandidateK: 50,
  hybridCandidateK: 50,
  rerankTopN: 25,
  rrfK: 60,
  indexVersionId: ""
};

type ErrorState = {
  status?: number;
  message: string;
  body?: unknown;
};

type SnapshotScenario = {
  scenario_id?: string;
  label?: string;
  query?: string;
  retrieval_mode?: SearchMode;
  result_count?: number;
  trace_id?: string;
};

export function SearchLab() {
  const snapshotMode = isSnapshotMode();
  const [formState, setFormState] = useState<SearchFormState>(initialState);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<ErrorState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [scenarios, setScenarios] = useState<SnapshotScenario[]>([]);
  const [scenarioError, setScenarioError] = useState<string | null>(null);

  useEffect(() => {
    if (!snapshotMode) {
      return;
    }
    let active = true;
    getSnapshotSearchScenarios()
      .then((data) => {
        if (active) {
          setScenarios(Array.isArray(data.items) ? (data.items as SnapshotScenario[]) : []);
          setScenarioError(null);
        }
      })
      .catch((caught) => {
        if (active) {
          setScenarioError(caught instanceof Error ? caught.message : "Snapshot search scenarios are unavailable.");
        }
      });
    return () => {
      active = false;
    };
  }, [snapshotMode]);

  async function executeSearch(request: SearchRequest) {
    setIsLoading(true);
    setError(null);
    setResponse(null);
    try {
      const result = await runSearch(request);
      setResponse(result);
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError({
          status: caught.status,
          message: caught.message,
          body: caught.body
        });
      } else if (caught instanceof TypeError) {
        setError({
          message: `Backend API is not reachable at ${API_BASE_URL}.`
        });
      } else {
        setError({
          message: caught instanceof Error ? caught.message : "Search request failed."
        });
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function submit(request: SearchRequest) {
    const nextValidationError = validateSearchForm(formState);
    setValidationError(nextValidationError);
    if (nextValidationError) {
      return;
    }

    await executeSearch(request);
  }

  async function loadSnapshotScenario(scenario: SnapshotScenario) {
    const nextState = {
      ...formState,
      query: scenario.query || "",
      retrievalMode: scenario.retrieval_mode || "bm25",
      topK: scenario.result_count || formState.topK
    };
    setFormState(nextState);
    setValidationError(null);
    await executeSearch(buildSearchRequest(nextState));
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge tone="neutral">Search Lab</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">Retrieval inspection console</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              {snapshotMode
                ? "Inspect real precomputed BM25, dense, hybrid, and reranked retrieval outputs exported from the full local Aletheia pipeline."
                : "Run BM25, dense, hybrid, and reranked retrieval against the FastAPI backend. Results are ranked chunks and score provenance only, with no answer generation."}
            </p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-400">
            {snapshotMode ? "Snapshot source" : "API base"}{" "}
            <span className="ml-2 font-mono text-slate-200">
              {snapshotMode ? "/demo-data/search-scenarios.json" : API_BASE_URL}
            </span>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,420px)_1fr]">
          <div className="space-y-4">
            {snapshotMode ? (
              <SnapshotScenarioPicker
                error={scenarioError}
                scenarios={scenarios}
                onSelect={(scenario) => void loadSnapshotScenario(scenario)}
              />
            ) : null}
            <SearchForm
              state={formState}
              validationError={validationError}
              isLoading={isLoading}
              isSnapshotMode={snapshotMode}
              onChange={setFormState}
              onSubmit={submit}
            />
            {response ? <SearchMetadataPanel response={response} /> : null}
            {response ? <LatencyPanel response={response} /> : null}
          </div>

          <div className="space-y-4">
            {error ? <ErrorCard error={error} /> : null}
            {isLoading ? <LoadingState /> : null}
            {!response && !error && !isLoading ? <InitialState /> : null}
            {response && !isLoading ? <SearchResults response={response} /> : null}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function InitialState() {
  const snapshotMode = isSnapshotMode();
  return (
    <Card>
      <CardHeader>
        <CardTitle>{snapshotMode ? "Ready for snapshot inspection" : "Ready for retrieval"}</CardTitle>
        <CardDescription>
          {snapshotMode
            ? "Select a curated precomputed search scenario to inspect exported results and trace links."
            : "Submit a query to run a real search request against FastAPI. No local fallback data is used."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-6 text-slate-400">
          {snapshotMode
            ? "This public snapshot includes real stored results only. Run the full local stack for arbitrary live retrieval."
            : "Use this lab to inspect ranking, score provenance, latency, query IDs, and trace IDs for the active retrieval infrastructure."}
        </p>
      </CardContent>
    </Card>
  );
}

function SnapshotScenarioPicker({
  scenarios,
  error,
  onSelect
}: {
  scenarios: SnapshotScenario[];
  error: string | null;
  onSelect: (scenario: SnapshotScenario) => void;
}) {
  return (
    <Card className="border-cyan-900/60 bg-cyan-950/10">
      <CardHeader>
        <CardTitle>Public demo scenarios</CardTitle>
        <CardDescription>
          These searches are real outputs exported from stored traces. Arbitrary live retrieval is disabled publicly.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        {scenarios.length ? (
          <div className="grid gap-2">
            {scenarios.map((scenario) => (
              <button
                className="rounded-md border border-slate-800 bg-slate-950/70 p-3 text-left transition hover:border-cyan-500/70 hover:bg-cyan-950/20 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                key={scenario.scenario_id || `${scenario.query}-${scenario.retrieval_mode}`}
                type="button"
                onClick={() => onSelect(scenario)}
              >
                <span className="block text-sm font-medium text-slate-100">
                  {scenario.label || scenario.query || "Snapshot scenario"}
                </span>
                <span className="mt-1 block text-xs text-slate-400">
                  {scenario.retrieval_mode ? getSearchModeLabel(scenario.retrieval_mode) : "Mode unavailable"} |{" "}
                  {scenario.result_count ?? 0} results
                </span>
                <span className="mt-2 inline-flex text-xs font-semibold text-cyan-200">Load exported results</span>
              </button>
            ))}
          </div>
        ) : !error ? (
          <p className="text-sm text-slate-400">Snapshot search scenarios are unavailable.</p>
        ) : null}
        <Button
          type="button"
          onClick={() => {
            if (scenarios[0]) {
              onSelect(scenarios[0]);
            }
          }}
          disabled={!scenarios.length}
        >
          Load first scenario
        </Button>
      </CardContent>
    </Card>
  );
}

function LoadingState() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Running retrieval</CardTitle>
        <CardDescription>The request is in flight. Hybrid rerank can take longer on first model load.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="h-24 animate-pulse rounded-md bg-slate-900" />
          <div className="h-24 animate-pulse rounded-md bg-slate-900" />
          <div className="h-24 animate-pulse rounded-md bg-slate-900" />
        </div>
      </CardContent>
    </Card>
  );
}

function ErrorCard({ error }: { error: ErrorState }) {
  return (
    <Card className="border-red-900 bg-red-950/20">
      <CardHeader>
        <CardTitle>Search request failed</CardTitle>
        <CardDescription>
          {error.status ? `FastAPI returned status ${error.status}.` : "The backend request did not complete."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-red-200">{error.message}</p>
        {error.body !== undefined ? (
          <pre className="max-h-72 overflow-auto rounded-md border border-red-900 bg-slate-950 p-3 text-xs text-slate-300">
            {typeof error.body === "string" ? error.body : JSON.stringify(error.body, null, 2)}
          </pre>
        ) : null}
      </CardContent>
    </Card>
  );
}
