import { formatCount, formatDate } from "@/components/indexes/index-format";
import { IndexStatusBadge } from "@/components/indexes/index-status-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { IndexVersionItem } from "@/lib/api/types";

type IndexVersionDetailProps = {
  version: IndexVersionItem | null;
};

export function IndexVersionDetail({ version }: IndexVersionDetailProps) {
  if (!version) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Select an index version</CardTitle>
          <CardDescription>No index version is selected.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-400">Details are shown only for real index versions returned by FastAPI.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <CardTitle>{version.name}</CardTitle>
          <IndexStatusBadge status={version.status} />
          {version.is_active ? <Badge tone="good">Active</Badge> : null}
        </div>
        <CardDescription className="font-mono">{version.id}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Detail label="Dataset ID" value={version.dataset_id} />
          <Detail label="Documents" value={formatCount(version.document_count)} />
          <Detail label="Chunks" value={formatCount(version.chunk_count)} />
          <Detail label="Vectors" value={formatCount(version.vector_count)} />
          <Detail label="Lexical index" value={version.lexical_index_name} />
          <Detail label="Vector collection" value={version.vector_collection_name} />
          <Detail label="Embedding model" value={version.embedding_model} />
          <Detail label="Embedding dimension" value={version.embedding_dimension} />
          <Detail label="Chunking strategy" value={version.chunking_strategy} />
          <Detail label="Chunking version" value={version.chunking_version} />
          <Detail label="Created" value={formatDate(version.created_at)} />
          <Detail label="Activated" value={formatDate(version.activated_at)} />
        </div>
        {version.notes ? <Detail label="Notes" value={version.notes} /> : null}
        {version.config_json ? (
          <details className="rounded-md border border-slate-800 bg-slate-950/70 p-3">
            <summary className="cursor-pointer text-sm font-medium text-slate-200">Raw config JSON</summary>
            <pre className="mt-3 max-h-72 overflow-auto text-xs text-slate-300">
              {JSON.stringify(version.config_json, null, 2)}
            </pre>
          </details>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Detail({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950/70 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 break-words text-sm text-slate-200">
        {value === null || value === undefined || value === "" ? "Unavailable" : String(value)}
      </div>
    </div>
  );
}
