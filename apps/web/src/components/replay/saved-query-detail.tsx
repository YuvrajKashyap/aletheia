import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ReplayJsonPanel } from "@/components/replay/replay-json-panel";
import type { SavedQueryDetail } from "@/lib/api/types";

function scalar(metadata: Record<string, unknown> | undefined, key: string) {
  const value = metadata?.[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : "Unavailable";
}

function list(metadata: Record<string, unknown> | undefined, key: string): string[] {
  const value = metadata?.[key];
  return Array.isArray(value) ? value.map((item) => String(item)) : [];
}

function datasetLabel(metadata: Record<string, unknown> | undefined) {
  const name = scalar(metadata, "dataset_name");
  const version = scalar(metadata, "dataset_version");
  if (name === "Unavailable" && version === "Unavailable") {
    return "Unavailable";
  }
  if (version === "Unavailable") {
    return name;
  }
  if (name === "Unavailable") {
    return version;
  }
  return `${name} ${version}`;
}

export function SavedQueryDetailPanel({ query }: { query: SavedQueryDetail | null }) {
  if (!query) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Select a saved query to inspect metadata and qrels context.</p>;
  }

  const relevantInternalIds = list(query.metadata_json, "relevant_document_ids");
  const relevantExternalIds = list(query.metadata_json, "relevant_document_external_ids");

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{query.name || "Saved query"}</CardTitle>
          <CardDescription>{query.source}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="rounded-md border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-200">
            {query.text}
          </p>
          <div className="grid gap-3 text-sm md:grid-cols-2">
            <Field label="Saved query ID" value={query.id} mono />
            <Field label="Dataset ID" value={query.dataset_id || "Unavailable"} mono />
            <Field label="Dataset" value={datasetLabel(query.metadata_json)} />
            <Field label="Benchmark query ID" value={scalar(query.metadata_json, "benchmark_query_id")} mono />
            <Field label="Query external ID" value={scalar(query.metadata_json, "query_external_id")} mono />
            <Field label="Relevance count" value={scalar(query.metadata_json, "relevance_count")} />
          </div>
          <DocumentList title="Relevant document external IDs" values={relevantExternalIds} />
          <DocumentList title="Relevant document IDs" values={relevantInternalIds} />
        </CardContent>
      </Card>
      <ReplayJsonPanel title="Saved query metadata" value={query.metadata_json} />
    </div>
  );
}

function Field({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <div className="text-slate-500">{label}</div>
      <div className={mono ? "break-all font-mono text-xs text-slate-300" : "text-slate-300"}>{value}</div>
    </div>
  );
}

function DocumentList({ title, values }: { title: string; values: string[] }) {
  return (
    <div>
      <div className="mb-2 text-sm text-slate-500">{title}</div>
      {values.length ? (
        <div className="flex max-h-32 flex-wrap gap-2 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3">
          {values.map((value) => (
            <span key={value} className="rounded border border-slate-800 bg-slate-900 px-2 py-1 font-mono text-xs text-slate-300">
              {value}
            </span>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-400">Unavailable</p>
      )}
    </div>
  );
}
