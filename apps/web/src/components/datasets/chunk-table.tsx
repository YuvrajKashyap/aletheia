import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { ChunkListItem } from "@/lib/api/types";

function shortId(value?: string | null) {
  return value ? value.slice(0, 8) : "Unavailable";
}

export function ChunkTable({
  chunks,
  onSelect,
  onDocumentFilter
}: {
  chunks: ChunkListItem[];
  onSelect: (chunkId: string) => void;
  onDocumentFilter?: (documentId: string) => void;
}) {
  if (!chunks.length) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">No chunks found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Index</TableHead>
            <TableHead>Chunk ID</TableHead>
            <TableHead>Document ID</TableHead>
            <TableHead>Tokens</TableHead>
            <TableHead>Strategy</TableHead>
            <TableHead>Text preview</TableHead>
            <TableHead className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
              Action
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {chunks.map((chunk) => (
            <TableRow key={chunk.id}>
              <TableCell>{chunk.chunk_index ?? "Unavailable"}</TableCell>
              <TableCell className="font-mono text-xs">{shortId(chunk.id)}</TableCell>
              <TableCell className="font-mono text-xs">
                {onDocumentFilter ? (
                  <button className="text-cyan-300 hover:text-cyan-100" onClick={() => onDocumentFilter(chunk.document_id)}>
                    {shortId(chunk.document_id)}
                  </button>
                ) : (
                  shortId(chunk.document_id)
                )}
              </TableCell>
              <TableCell>{chunk.token_count ?? "Unavailable"}</TableCell>
              <TableCell className="whitespace-nowrap text-xs">
                {chunk.chunking_strategy || "Unavailable"} {chunk.chunking_version || ""}
              </TableCell>
              <TableCell className="min-w-96 max-w-xl text-slate-400">{chunk.text_preview || chunk.text || "Unavailable"}</TableCell>
              <TableCell className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
                <Button variant="secondary" onClick={() => onSelect(chunk.id)}>
                  View detail
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
