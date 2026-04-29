import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { OperationalStatusBadge } from "@/components/system/operational-status-badge";
import type { ModelStatusResponse } from "@/lib/api/types";

export function ModelStatusPanel({
  embedding,
  embeddingError,
  reranker,
  rerankerError,
  snapshotMode = false
}: {
  embedding: ModelStatusResponse | null;
  embeddingError?: string | null;
  reranker: ModelStatusResponse | null;
  rerankerError?: string | null;
  snapshotMode?: boolean;
}) {
  if (snapshotMode) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Model status</CardTitle>
          <CardDescription>
            Models are used by the full local stack, not loaded in the hosted snapshot.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 lg:grid-cols-2">
          <SnapshotModelCard title="Embedding model" modelName="BAAI/bge-small-en-v1.5" />
          <SnapshotModelCard title="Reranker model" modelName="cross-encoder/ms-marco-MiniLM-L-6-v2" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Model status</CardTitle>
        <CardDescription>Backend-reported embedding and reranker model state.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 lg:grid-cols-2">
        <ModelCard title="Embedding model" model={embedding} error={embeddingError} showDimension />
        <ModelCard title="Reranker model" model={reranker} error={rerankerError} />
      </CardContent>
    </Card>
  );
}

function SnapshotModelCard({ title, modelName }: { title: string; modelName: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
        <OperationalStatusBadge status="warning" />
      </div>
      <div className="mt-4 space-y-2 text-sm">
        <Field label="Model" value={modelName} />
        <Field label="Status" value="local full stack only" />
        <Field label="Hosted snapshot" value="not loaded publicly" />
      </div>
    </div>
  );
}

function ModelCard({
  title,
  model,
  error,
  showDimension = false
}: {
  title: string;
  model: ModelStatusResponse | null;
  error?: string | null;
  showDimension?: boolean;
}) {
  const status = error || model?.error ? "error" : model?.loaded ? "healthy" : model ? "warning" : "unknown";
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
        <OperationalStatusBadge status={status} />
      </div>
      <div className="mt-4 space-y-2 text-sm">
        <Field label="Model" value={model?.model_name} />
        <Field label="Loaded" value={model?.loaded} />
        <Field label="Device" value={model?.device} />
        {showDimension ? <Field label="Dimension" value={model?.embedding_dimension} /> : null}
        <Field label="Cache" value={model?.cache_dir} mono />
        {error || model?.error ? <Field label="Error" value={error || model?.error} tone="error" /> : null}
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  mono = false,
  tone = "normal"
}: {
  label: string;
  value?: string | number | boolean | null;
  mono?: boolean;
  tone?: "normal" | "error";
}) {
  return (
    <div className="grid gap-2 md:grid-cols-[100px_1fr]">
      <div className="text-slate-500">{label}</div>
      <div className={`${mono ? "font-mono text-xs" : ""} ${tone === "error" ? "break-all text-red-300" : "break-all text-slate-200"}`}>
        {value === null || value === undefined || value === "" ? "Unavailable" : String(value)}
      </div>
    </div>
  );
}
