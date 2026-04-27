"use client";

import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { LatencyPanel } from "@/components/search/latency-panel";
import { SearchForm, type SearchFormState, validateSearchForm } from "@/components/search/search-form";
import { SearchMetadataPanel } from "@/components/search/search-metadata-panel";
import { SearchResults } from "@/components/search/search-results";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import { runSearch } from "@/lib/api/search";
import type { SearchRequest, SearchResponse } from "@/lib/api/types";
import { API_BASE_URL } from "@/lib/config";

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

export function SearchLab() {
  const [formState, setFormState] = useState<SearchFormState>(initialState);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<ErrorState | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function submit(request: SearchRequest) {
    const nextValidationError = validateSearchForm(formState);
    setValidationError(nextValidationError);
    if (nextValidationError) {
      return;
    }

    setIsLoading(true);
    setError(null);
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

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge tone="neutral">Search Lab</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">Retrieval inspection console</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Run BM25, dense, hybrid, and reranked retrieval against the FastAPI backend. Results are ranked chunks and
              score provenance only, with no answer generation.
            </p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-400">
            API base <span className="ml-2 font-mono text-slate-200">{API_BASE_URL}</span>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,420px)_1fr]">
          <div className="space-y-4">
            <SearchForm
              state={formState}
              validationError={validationError}
              isLoading={isLoading}
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
  return (
    <Card>
      <CardHeader>
        <CardTitle>Ready for retrieval</CardTitle>
        <CardDescription>
          Submit a query to run a real search request against FastAPI. No local fallback data is used.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-6 text-slate-400">
          Use this lab to inspect ranking, score provenance, latency, query IDs, and trace IDs for the active retrieval
          infrastructure.
        </p>
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
