import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MetadataJsonPanel } from "@/components/datasets/metadata-json-panel";
import type { ChunkDetailResponse } from "@/lib/api/types";

export function ChunkDetailPanel({
  chunk,
  loading,
  error,
  onParentDocument
}: {
  chunk: ChunkDetailResponse | null;
  loading?: boolean;
  error?: string | null;
  onParentDocument?: (documentId: string) => void;
}) {
  if (loading) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Loading chunk detail...</p>;
  }

  if (error) {
    return <p className="rounded-lg border border-red-900/70 p-4 text-sm text-red-300">{error}</p>;
  }

  if (!chunk) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">Select a chunk to inspect full stored text.</p>;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Chunk {chunk.chunk_index ?? "Unavailable"}</CardTitle>
          <CardDescription>
            {chunk.chunking_strategy || "Unknown strategy"} {chunk.chunking_version || ""}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 text-sm md:grid-cols-2">
            <div>
              <div className="text-slate-500">Chunk ID</div>
              <div className="font-mono text-xs text-slate-300">{chunk.id}</div>
            </div>
            <div>
              <div className="text-slate-500">Document ID</div>
              {onParentDocument ? (
                <button className="font-mono text-xs text-cyan-300 hover:text-cyan-100" onClick={() => onParentDocument(chunk.document_id)}>
                  {chunk.document_id}
                </button>
              ) : (
                <div className="font-mono text-xs text-slate-300">{chunk.document_id}</div>
              )}
            </div>
            <div>
              <div className="text-slate-500">Token count</div>
              <div className="text-slate-300">{chunk.token_count ?? "Unavailable"}</div>
            </div>
            <div>
              <div className="text-slate-500">Character range</div>
              <div className="text-slate-300">
                {chunk.char_start ?? "?"} to {chunk.char_end ?? "?"}
              </div>
            </div>
            <div className="md:col-span-2">
              <div className="text-slate-500">Content hash</div>
              <div className="font-mono text-xs text-slate-300">{chunk.content_hash || "Unavailable"}</div>
            </div>
          </div>
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-300">
            {chunk.text}
          </pre>
        </CardContent>
      </Card>
      <MetadataJsonPanel value={chunk.metadata_json} />
    </div>
  );
}
