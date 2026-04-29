"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BenchmarkQueryDetailPanel } from "@/components/datasets/benchmark-query-detail-panel";
import { BenchmarkQueryTable } from "@/components/datasets/benchmark-query-table";
import { ChunkDetailPanel } from "@/components/datasets/chunk-detail-panel";
import { ChunkTable } from "@/components/datasets/chunk-table";
import { CorpusSearchControls } from "@/components/datasets/corpus-search-controls";
import { DatasetOverviewCards } from "@/components/datasets/dataset-overview-cards";
import { DatasetSelector } from "@/components/datasets/dataset-selector";
import { DatasetTabs, type DatasetTab } from "@/components/datasets/dataset-tabs";
import { DocumentDetailPanel } from "@/components/datasets/document-detail-panel";
import { DocumentTable } from "@/components/datasets/document-table";
import { RelevanceJudgmentTable } from "@/components/datasets/relevance-judgment-table";
import {
  getBenchmarkQueries,
  getBenchmarkQuery,
  getChunk,
  getChunks,
  getDatasetStats,
  getDatasets,
  getDocument,
  getDocuments,
  getRelevanceJudgments
} from "@/lib/api/datasets";
import { API_BASE_URL } from "@/lib/config";
import { isSnapshotMode } from "@/lib/demo-mode";
import type {
  BenchmarkQueryDetailResponse,
  BenchmarkQueryListItem,
  ChunkDetailResponse,
  ChunkListItem,
  DatasetListResponse,
  DatasetStatsResponse,
  DatasetSummary,
  DocumentDetailResponse,
  DocumentListItem,
  RelevanceJudgmentItem
} from "@/lib/api/types";

type PageState<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  loading: boolean;
  error: string | null;
};

function emptyPage<T>(limit = 25): PageState<T> {
  return { items: [], total: 0, limit, offset: 0, loading: false, error: null };
}

function errorMessage(error: unknown) {
  if (error instanceof TypeError && error.message.toLowerCase().includes("fetch")) {
    return `Backend API is not reachable at ${API_BASE_URL}.`;
  }
  if (error instanceof Error && error.message.toLowerCase() === "failed to fetch") {
    return `Backend API is not reachable at ${API_BASE_URL}.`;
  }
  return error instanceof Error ? error.message : "Request failed";
}

function normalizeDatasets(response: DatasetListResponse): DatasetSummary[] {
  return Array.isArray(response) ? response : response.items || [];
}

export function DatasetBrowser() {
  const snapshotMode = isSnapshotMode();
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [stats, setStats] = useState<DatasetStatsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<DatasetTab>("documents");
  const [topError, setTopError] = useState<string | null>(null);
  const [loadingDatasets, setLoadingDatasets] = useState(false);

  const [documents, setDocuments] = useState<PageState<DocumentListItem>>(emptyPage());
  const [chunks, setChunks] = useState<PageState<ChunkListItem>>(emptyPage());
  const [queries, setQueries] = useState<PageState<BenchmarkQueryListItem>>(emptyPage());
  const [qrels, setQrels] = useState<PageState<RelevanceJudgmentItem>>(emptyPage());

  const [selectedDocument, setSelectedDocument] = useState<DocumentDetailResponse | null>(null);
  const [documentChunks, setDocumentChunks] = useState<ChunkListItem[]>([]);
  const [documentDetailState, setDocumentDetailState] = useState({ loading: false, error: null as string | null });

  const [selectedChunk, setSelectedChunk] = useState<ChunkDetailResponse | null>(null);
  const [chunkDetailState, setChunkDetailState] = useState({ loading: false, error: null as string | null });

  const [selectedQuery, setSelectedQuery] = useState<BenchmarkQueryDetailResponse | null>(null);
  const [queryJudgments, setQueryJudgments] = useState<RelevanceJudgmentItem[]>([]);
  const [queryDetailState, setQueryDetailState] = useState({ loading: false, error: null as string | null });

  const [queryExternalId, setQueryExternalId] = useState("");
  const [documentExternalId, setDocumentExternalId] = useState("");
  const [appliedQrelFilters, setAppliedQrelFilters] = useState({ queryExternalId: "", documentExternalId: "" });

  const selectedDataset = useMemo(
    () => datasets.find((dataset) => dataset.id === selectedDatasetId) ?? null,
    [datasets, selectedDatasetId]
  );

  const loadDatasets = useCallback(async () => {
    setLoadingDatasets(true);
    setTopError(null);
    try {
      const response = await getDatasets();
      const items = normalizeDatasets(response);
      setDatasets(items);
      setSelectedDatasetId((current) => current ?? items[0]?.id ?? null);
    } catch (error) {
      setTopError(errorMessage(error));
      setDatasets([]);
      setSelectedDatasetId(null);
    } finally {
      setLoadingDatasets(false);
    }
  }, []);

  const loadStats = useCallback(async (datasetId: string) => {
    try {
      setStats(await getDatasetStats(datasetId));
    } catch {
      setStats(null);
    }
  }, []);

  const loadDocuments = useCallback(async (datasetId: string, limit: number, offset: number) => {
    setDocuments((current) => ({ ...current, loading: true, error: null, limit, offset }));
    try {
      const response = await getDocuments({ datasetId, limit, offset });
      setDocuments({ items: response.items, total: response.total, limit: response.limit, offset: response.offset, loading: false, error: null });
    } catch (error) {
      setDocuments((current) => ({ ...current, loading: false, error: errorMessage(error), items: [], total: 0 }));
    }
  }, []);

  const loadChunks = useCallback(async (datasetId: string, limit: number, offset: number) => {
    setChunks((current) => ({ ...current, loading: true, error: null, limit, offset }));
    try {
      const response = await getChunks({ datasetId, limit, offset });
      setChunks({ items: response.items, total: response.total, limit: response.limit, offset: response.offset, loading: false, error: null });
    } catch (error) {
      setChunks((current) => ({ ...current, loading: false, error: errorMessage(error), items: [], total: 0 }));
    }
  }, []);

  const loadQueries = useCallback(async (datasetId: string, limit: number, offset: number) => {
    setQueries((current) => ({ ...current, loading: true, error: null, limit, offset }));
    try {
      const response = await getBenchmarkQueries({ datasetId, limit, offset });
      setQueries({ items: response.items, total: response.total, limit: response.limit, offset: response.offset, loading: false, error: null });
    } catch (error) {
      setQueries((current) => ({ ...current, loading: false, error: errorMessage(error), items: [], total: 0 }));
    }
  }, []);

  const loadQrels = useCallback(
    async (datasetId: string, limit: number, offset: number) => {
      setQrels((current) => ({ ...current, loading: true, error: null, limit, offset }));
      try {
        const response = await getRelevanceJudgments({
          datasetId,
          queryExternalId: appliedQrelFilters.queryExternalId,
          documentExternalId: appliedQrelFilters.documentExternalId,
          limit,
          offset
        });
        setQrels({ items: response.items, total: response.total, limit: response.limit, offset: response.offset, loading: false, error: null });
      } catch (error) {
        setQrels((current) => ({ ...current, loading: false, error: errorMessage(error), items: [], total: 0 }));
      }
    },
    [appliedQrelFilters]
  );

  useEffect(() => {
    void loadDatasets();
  }, [loadDatasets]);

  useEffect(() => {
    if (!selectedDatasetId) {
      return;
    }
    void loadStats(selectedDatasetId);
    void loadDocuments(selectedDatasetId, documents.limit, 0);
    void loadChunks(selectedDatasetId, chunks.limit, 0);
    void loadQueries(selectedDatasetId, queries.limit, 0);
    void loadQrels(selectedDatasetId, qrels.limit, 0);
    setSelectedDocument(null);
    setSelectedChunk(null);
    setSelectedQuery(null);
  }, [
    selectedDatasetId,
    loadStats,
    loadDocuments,
    loadChunks,
    loadQueries,
    loadQrels,
    documents.limit,
    chunks.limit,
    queries.limit,
    qrels.limit
  ]);

  useEffect(() => {
    if (selectedDatasetId) {
      void loadQrels(selectedDatasetId, qrels.limit, 0);
    }
  }, [appliedQrelFilters, loadQrels, qrels.limit, selectedDatasetId]);

  async function selectDocument(documentId: string) {
    setDocumentDetailState({ loading: true, error: null });
    setSelectedDocument(null);
    setDocumentChunks([]);
    try {
      const [document, chunkList] = await Promise.all([
        getDocument(documentId),
        getChunks({ documentId, limit: 50, offset: 0 })
      ]);
      setSelectedDocument(document);
      setDocumentChunks(chunkList.items);
    } catch (error) {
      setDocumentDetailState({ loading: false, error: errorMessage(error) });
      return;
    }
    setDocumentDetailState({ loading: false, error: null });
  }

  async function selectChunk(chunkId: string) {
    setChunkDetailState({ loading: true, error: null });
    setSelectedChunk(null);
    try {
      setSelectedChunk(await getChunk(chunkId));
    } catch (error) {
      setChunkDetailState({ loading: false, error: errorMessage(error) });
      return;
    }
    setChunkDetailState({ loading: false, error: null });
  }

  async function selectQuery(queryId: string) {
    setQueryDetailState({ loading: true, error: null });
    setSelectedQuery(null);
    setQueryJudgments([]);
    try {
      const [query, judgments] = await Promise.all([
        getBenchmarkQuery(queryId),
        getRelevanceJudgments({ queryId, limit: 50, offset: 0 })
      ]);
      setSelectedQuery(query);
      setQueryJudgments(judgments.items);
    } catch (error) {
      setQueryDetailState({ loading: false, error: errorMessage(error) });
      return;
    }
    setQueryDetailState({ loading: false, error: null });
  }

  function refreshCurrent() {
    if (!selectedDatasetId) {
      void loadDatasets();
      return;
    }
    void loadStats(selectedDatasetId);
    if (activeTab === "documents") void loadDocuments(selectedDatasetId, documents.limit, documents.offset);
    if (activeTab === "chunks") void loadChunks(selectedDatasetId, chunks.limit, chunks.offset);
    if (activeTab === "queries") void loadQueries(selectedDatasetId, queries.limit, queries.offset);
    if (activeTab === "qrels") void loadQrels(selectedDatasetId, qrels.limit, qrels.offset);
  }

  const tabContent = (() => {
    if (!selectedDatasetId) {
      return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">No dataset selected.</p>;
    }

    if (activeTab === "documents") {
      return (
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
          <div className="space-y-3">
            <CorpusSearchControls
              total={documents.total}
              limit={documents.limit}
              offset={documents.offset}
              onLimitChange={(limit) => loadDocuments(selectedDatasetId, limit, 0)}
              onPrevious={() => loadDocuments(selectedDatasetId, documents.limit, Math.max(0, documents.offset - documents.limit))}
              onNext={() => loadDocuments(selectedDatasetId, documents.limit, documents.offset + documents.limit)}
            />
            {documents.error ? <p className="rounded-lg border border-red-900/70 p-4 text-sm text-red-300">{documents.error}</p> : null}
            {documents.loading ? <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading documents...</p> : <DocumentTable documents={documents.items} onSelect={selectDocument} />}
          </div>
          <DocumentDetailPanel
            document={selectedDocument}
            chunks={documentChunks}
            loading={documentDetailState.loading}
            error={documentDetailState.error}
            onChunkSelect={(chunkId) => {
              setActiveTab("chunks");
              void selectChunk(chunkId);
            }}
          />
        </div>
      );
    }

    if (activeTab === "chunks") {
      return (
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
          <div className="space-y-3">
            <CorpusSearchControls
              total={chunks.total}
              limit={chunks.limit}
              offset={chunks.offset}
              onLimitChange={(limit) => loadChunks(selectedDatasetId, limit, 0)}
              onPrevious={() => loadChunks(selectedDatasetId, chunks.limit, Math.max(0, chunks.offset - chunks.limit))}
              onNext={() => loadChunks(selectedDatasetId, chunks.limit, chunks.offset + chunks.limit)}
            />
            {chunks.error ? <p className="rounded-lg border border-red-900/70 p-4 text-sm text-red-300">{chunks.error}</p> : null}
            {chunks.loading ? (
              <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading chunks...</p>
            ) : (
              <ChunkTable chunks={chunks.items} onSelect={selectChunk} onDocumentFilter={selectDocument} />
            )}
          </div>
          <ChunkDetailPanel
            chunk={selectedChunk}
            loading={chunkDetailState.loading}
            error={chunkDetailState.error}
            onParentDocument={(documentId) => {
              setActiveTab("documents");
              void selectDocument(documentId);
            }}
          />
        </div>
      );
    }

    if (activeTab === "queries") {
      return (
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
          <div className="space-y-3">
            <CorpusSearchControls
              total={queries.total}
              limit={queries.limit}
              offset={queries.offset}
              onLimitChange={(limit) => loadQueries(selectedDatasetId, limit, 0)}
              onPrevious={() => loadQueries(selectedDatasetId, queries.limit, Math.max(0, queries.offset - queries.limit))}
              onNext={() => loadQueries(selectedDatasetId, queries.limit, queries.offset + queries.limit)}
            />
            {queries.error ? <p className="rounded-lg border border-red-900/70 p-4 text-sm text-red-300">{queries.error}</p> : null}
            {queries.loading ? <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading benchmark queries...</p> : <BenchmarkQueryTable queries={queries.items} onSelect={selectQuery} />}
          </div>
          <BenchmarkQueryDetailPanel
            query={selectedQuery}
            judgments={queryJudgments}
            loading={queryDetailState.loading}
            error={queryDetailState.error}
          />
        </div>
      );
    }

    return (
      <div className="space-y-3">
        <CorpusSearchControls
          total={qrels.total}
          limit={qrels.limit}
          offset={qrels.offset}
          onLimitChange={(limit) => loadQrels(selectedDatasetId, limit, 0)}
          onPrevious={() => loadQrels(selectedDatasetId, qrels.limit, Math.max(0, qrels.offset - qrels.limit))}
          onNext={() => loadQrels(selectedDatasetId, qrels.limit, qrels.offset + qrels.limit)}
        >
          <label className="text-xs text-slate-500">
            Query external ID
            <input
              className="ml-2 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-100"
              placeholder="exact ID"
              value={queryExternalId}
              onChange={(event) => setQueryExternalId(event.target.value)}
            />
          </label>
          <label className="text-xs text-slate-500">
            Document external ID
            <input
              className="ml-2 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-100"
              placeholder="exact ID"
              value={documentExternalId}
              onChange={(event) => setDocumentExternalId(event.target.value)}
            />
          </label>
          <Button
            variant="secondary"
            onClick={() =>
              setAppliedQrelFilters({
                queryExternalId: queryExternalId.trim(),
                documentExternalId: documentExternalId.trim()
              })
            }
          >
            Apply filters
          </Button>
        </CorpusSearchControls>
        <p className="text-xs text-slate-500">
          Use exact query or document external IDs, for example 659 or 1215116.
        </p>
        {qrels.error ? <p className="rounded-lg border border-red-900/70 p-4 text-sm text-red-300">{qrels.error}</p> : null}
        {qrels.loading ? <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading relevance judgments...</p> : <RelevanceJudgmentTable judgments={qrels.items} />}
      </div>
    );
  })();

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="space-y-3">
          <Badge tone="neutral">Dataset Browser</Badge>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">Datasets</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                {snapshotMode
                  ? "Inspect representative exported corpus samples, benchmark queries, and qrels generated from the full local stack."
                  : "Inspect real corpus records, chunks, benchmark queries, and qrels served by FastAPI."}
              </p>
              <div className="mt-2 font-mono text-xs text-slate-500">
                {snapshotMode ? "Snapshot source: /demo-data dataset samples" : `Backend: ${API_BASE_URL}`}
              </div>
            </div>
            <Button onClick={refreshCurrent} disabled={loadingDatasets}>
              Refresh
            </Button>
          </div>
        </section>

        {snapshotMode ? (
          <Card className="border-cyan-900/60 bg-cyan-950/10">
            <CardHeader>
              <CardTitle>Public dataset sample</CardTitle>
              <CardDescription>
                Public demo mode shows a representative exported sample. The full local dataset contains 5,183
                documents, 5,183 chunks, 300 benchmark queries, and 339 qrels.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : null}

        {topError ? (
          <Card>
            <CardHeader>
              <CardTitle>Dataset Browser request failed</CardTitle>
              <CardDescription>Backend data unavailable</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-red-300">{topError}</p>
            </CardContent>
          </Card>
        ) : null}

        <section className="flex flex-col gap-4 rounded-lg border border-slate-800 bg-slate-950/70 p-4 md:flex-row md:items-end md:justify-between">
          <DatasetSelector datasets={datasets} selectedDatasetId={selectedDatasetId} onChange={setSelectedDatasetId} />
          <p className="text-sm text-slate-500">
            {loadingDatasets ? "Loading datasets..." : `${datasets.length} dataset${datasets.length === 1 ? "" : "s"} loaded.`}
          </p>
        </section>

        <DatasetOverviewCards dataset={selectedDataset} stats={stats} />

        <section className="space-y-4">
          <DatasetTabs activeTab={activeTab} onChange={setActiveTab} />
          {tabContent}
        </section>
      </div>
    </AppShell>
  );
}
