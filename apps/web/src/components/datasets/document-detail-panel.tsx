import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ChunkListItem, DocumentDetailResponse } from "@/lib/api/types";
import { MetadataJsonPanel } from "@/components/datasets/metadata-json-panel";
import { ChunkTable } from "@/components/datasets/chunk-table";

export function DocumentDetailPanel({
  document,
  chunks,
  loading,
  error,
  onChunkSelect
}: {
  document: DocumentDetailResponse | null;
  chunks: ChunkListItem[];
  loading?: boolean;
  error?: string | null;
  onChunkSelect: (chunkId: string) => void;
}) {
  if (loading) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading document detail...</p>;
  }

  if (error) {
    return <p className="rounded-lg border border-red-900/70 p-4 text-sm text-red-300">{error}</p>;
  }

  if (!document) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Select a document to inspect full text and chunks.</p>;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{document.title || "Untitled document"}</CardTitle>
          <CardDescription>
            External ID {document.external_id} · {document.chunk_count ?? "Unavailable"} chunks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 text-sm md:grid-cols-2">
            <div>
              <div className="text-slate-500">Document ID</div>
              <div className="font-mono text-xs text-slate-300">{document.id}</div>
            </div>
            <div>
              <div className="text-slate-500">Dataset ID</div>
              <div className="font-mono text-xs text-slate-300">{document.dataset_id}</div>
            </div>
          </div>
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-300">
            {document.text}
          </pre>
        </CardContent>
      </Card>
      <MetadataJsonPanel value={document.metadata_json} />
      <Card>
        <CardHeader>
          <CardTitle>Document Chunks</CardTitle>
          <CardDescription>Chunks loaded from FastAPI for the selected document</CardDescription>
        </CardHeader>
        <CardContent>
          <ChunkTable chunks={chunks} onSelect={onChunkSelect} />
        </CardContent>
      </Card>
    </div>
  );
}
