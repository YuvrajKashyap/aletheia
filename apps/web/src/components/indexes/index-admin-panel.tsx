"use client";

import { useState } from "react";

import { IndexJobStatus } from "@/components/indexes/index-job-status";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import {
  activateIndexVersion,
  buildLexicalIndex,
  buildVectorIndex,
  createIndexVersion,
  getJobStatus,
  markIndexVersionReady,
  rollbackIndexVersion
} from "@/lib/api/indexes";
import type { BuildIndexJobResponse, IndexVersionItem, JobStatusResponse } from "@/lib/api/types";
import { isSnapshotMode } from "@/lib/demo-mode";

type IndexAdminPanelProps = {
  selectedVersion: IndexVersionItem | null;
  onChanged: () => void;
};

export function IndexAdminPanel({ selectedVersion, onChanged }: IndexAdminPanelProps) {
  const snapshotMode = isSnapshotMode();
  const [isOpen, setIsOpen] = useState(false);
  const [adminApiKey, setAdminApiKey] = useState("");
  const [datasetName, setDatasetName] = useState("beir/scifact");
  const [datasetVersion, setDatasetVersion] = useState("test");
  const [chunkingStrategy, setChunkingStrategy] = useState("scifact_document_v1");
  const [chunkingVersion, setChunkingVersion] = useState("1.0");
  const [embeddingModel, setEmbeddingModel] = useState("BAAI/bge-small-en-v1.5");
  const [notes, setNotes] = useState("Created from local Index Console UI");
  const [lexicalRecreate, setLexicalRecreate] = useState(false);
  const [lexicalLimit, setLexicalLimit] = useState("");
  const [lexicalRefresh, setLexicalRefresh] = useState(true);
  const [vectorRecreate, setVectorRecreate] = useState(false);
  const [vectorLimit, setVectorLimit] = useState("");
  const [vectorBatchSize, setVectorBatchSize] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [buildJob, setBuildJob] = useState<BuildIndexJobResponse | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [jobLoading, setJobLoading] = useState(false);
  const [jobError, setJobError] = useState<string | null>(null);

  if (snapshotMode) {
    return (
      <Card className="border-slate-800 bg-slate-950/70">
        <CardHeader>
          <CardTitle>Admin actions disabled</CardTitle>
          <CardDescription>
            Index admin actions are disabled in public snapshot mode. Snapshot data shows index metadata exported from
            the full local stack. Run locally to create, activate, rollback, or rebuild indexes.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  async function runMutation(action: () => Promise<unknown>, success: string) {
    setIsSubmitting(true);
    setError(null);
    setMessage(null);
    try {
      await action();
      setMessage(success);
      onChanged();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createVersion() {
    await runMutation(
      () =>
        createIndexVersion(
          {
            dataset_name: datasetName,
            dataset_version: datasetVersion,
            embedding_model: embeddingModel,
            chunking_strategy: chunkingStrategy,
            chunking_version: chunkingVersion,
            notes
          },
          adminApiKey
        ),
      "Index version metadata created."
    );
  }

  async function startBuild(kind: "lexical" | "vector") {
    if (!selectedVersion) {
      setError("Select an index version first.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    setMessage(null);
    setBuildJob(null);
    setJobStatus(null);
    setJobError(null);
    try {
      const response =
        kind === "lexical"
          ? await buildLexicalIndex(
              selectedVersion.id,
              {
                recreate: lexicalRecreate,
                limit: parseOptionalInt(lexicalLimit),
                refresh: lexicalRefresh
              },
              adminApiKey
            )
          : await buildVectorIndex(
              selectedVersion.id,
              {
                recreate: vectorRecreate,
                limit: parseOptionalInt(vectorLimit),
                batch_size: parseOptionalInt(vectorBatchSize)
              },
              adminApiKey
            );
      setBuildJob(response);
      setMessage(response.message || `${kind} build job queued.`);
      onChanged();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function refreshJob() {
    if (!buildJob?.job_id) {
      return;
    }
    setJobLoading(true);
    setJobError(null);
    try {
      setJobStatus(await getJobStatus(buildJob.job_id));
      onChanged();
    } catch (caught) {
      setJobError(errorMessage(caught));
    } finally {
      setJobLoading(false);
    }
  }

  const blocked = isSubmitting || !adminApiKey.trim();

  return (
    <Card className="border-slate-800 bg-slate-950/70">
      <CardHeader>
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <CardTitle>Local admin actions</CardTitle>
            <CardDescription>Actions call real admin-protected FastAPI endpoints. The key stays in component state.</CardDescription>
          </div>
          <Button type="button" onClick={() => setIsOpen((current) => !current)}>
            {isOpen ? "Hide actions" : "Show actions"}
          </Button>
        </div>
      </CardHeader>
      {isOpen ? (
        <CardContent className="space-y-5">
          <label className="grid gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Admin API key</span>
            <input className={inputClass} type="password" value={adminApiKey} onChange={(event) => setAdminApiKey(event.target.value)} />
          </label>

          <section className="space-y-3 rounded-md border border-slate-800 bg-slate-950/60 p-3">
            <h3 className="text-sm font-medium text-slate-100">Create metadata index version</h3>
            <div className="grid gap-3 md:grid-cols-2">
              <Field label="Dataset name" value={datasetName} onChange={setDatasetName} />
              <Field label="Dataset version" value={datasetVersion} onChange={setDatasetVersion} />
              <Field label="Chunking strategy" value={chunkingStrategy} onChange={setChunkingStrategy} />
              <Field label="Chunking version" value={chunkingVersion} onChange={setChunkingVersion} />
              <Field label="Embedding model" value={embeddingModel} onChange={setEmbeddingModel} />
              <Field label="Notes" value={notes} onChange={setNotes} />
            </div>
            <Button disabled={blocked} type="button" onClick={createVersion}>
              Create index version
            </Button>
          </section>

          <section className="space-y-3 rounded-md border border-slate-800 bg-slate-950/60 p-3">
            <h3 className="text-sm font-medium text-slate-100">Selected version actions</h3>
            <p className="break-all font-mono text-xs text-slate-500">{selectedVersion?.id || "No selected version"}</p>
            <div className="flex flex-wrap gap-2">
              <Button disabled={blocked || !selectedVersion} type="button" onClick={() => runMutation(() => markIndexVersionReady(selectedVersion!.id, adminApiKey), "Index version marked ready.")}>
                Mark ready
              </Button>
              <Button disabled={blocked || !selectedVersion} type="button" onClick={() => runMutation(() => activateIndexVersion(selectedVersion!.id, adminApiKey), "Index version activated.")}>
                Activate
              </Button>
              <Button disabled={blocked || !selectedVersion} type="button" onClick={() => runMutation(() => rollbackIndexVersion(selectedVersion!.id, adminApiKey), "Rollback activated.")}>
                Rollback
              </Button>
            </div>
          </section>

          <section className="grid gap-3 lg:grid-cols-2">
            <BuildPanel
              title="Build lexical index"
              recreate={lexicalRecreate}
              limit={lexicalLimit}
              extraLabel="Refresh OpenSearch"
              extraValue={lexicalRefresh}
              onExtraChange={setLexicalRefresh}
              onLimitChange={setLexicalLimit}
              onRecreateChange={setLexicalRecreate}
              onSubmit={() => startBuild("lexical")}
              disabled={blocked || !selectedVersion}
            />
            <BuildPanel
              title="Build vector index"
              recreate={vectorRecreate}
              limit={vectorLimit}
              batchSize={vectorBatchSize}
              onBatchSizeChange={setVectorBatchSize}
              onLimitChange={setVectorLimit}
              onRecreateChange={setVectorRecreate}
              onSubmit={() => startBuild("vector")}
              disabled={blocked || !selectedVersion}
            />
          </section>

          {message ? <p className="text-sm text-emerald-300">{message}</p> : null}
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
          <IndexJobStatus buildJob={buildJob} error={jobError} isLoading={jobLoading} jobStatus={jobStatus} onRefresh={refreshJob} />
        </CardContent>
      ) : null}
    </Card>
  );
}

const inputClass =
  "rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20";

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="grid gap-2">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <input className={inputClass} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function BuildPanel({
  title,
  recreate,
  limit,
  batchSize,
  extraLabel,
  extraValue,
  disabled,
  onRecreateChange,
  onLimitChange,
  onBatchSizeChange,
  onExtraChange,
  onSubmit
}: {
  title: string;
  recreate: boolean;
  limit: string;
  batchSize?: string;
  extraLabel?: string;
  extraValue?: boolean;
  disabled: boolean;
  onRecreateChange: (value: boolean) => void;
  onLimitChange: (value: string) => void;
  onBatchSizeChange?: (value: string) => void;
  onExtraChange?: (value: boolean) => void;
  onSubmit: () => void;
}) {
  return (
    <div className="space-y-3 rounded-md border border-slate-800 bg-slate-950/60 p-3">
      <h3 className="text-sm font-medium text-slate-100">{title}</h3>
      <label className="flex items-center gap-2 text-sm text-slate-300">
        <input checked={recreate} type="checkbox" onChange={(event) => onRecreateChange(event.target.checked)} />
        Recreate
      </label>
      <Field label="Optional limit" value={limit} onChange={onLimitChange} />
      {onBatchSizeChange ? <Field label="Optional batch size" value={batchSize || ""} onChange={onBatchSizeChange} /> : null}
      {extraLabel && onExtraChange ? (
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input checked={Boolean(extraValue)} type="checkbox" onChange={(event) => onExtraChange(event.target.checked)} />
          {extraLabel}
        </label>
      ) : null}
      <Button disabled={disabled} type="button" onClick={onSubmit}>
        {title}
      </Button>
    </div>
  );
}

function parseOptionalInt(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function errorMessage(caught: unknown): string {
  if (caught instanceof ApiError) {
    return caught.status === 401 || caught.status === 403 ? "Admin API key was rejected by FastAPI." : caught.message;
  }
  return caught instanceof Error ? caught.message : "Request failed.";
}
