import { formatCount, formatDate, shortId } from "@/components/indexes/index-format";
import { IndexStatusBadge } from "@/components/indexes/index-status-badge";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { IndexVersionItem } from "@/lib/api/types";

type IndexVersionTableProps = {
  versions: IndexVersionItem[];
  selectedVersionId: string | null;
  onSelect: (id: string) => void;
};

export function IndexVersionTable({ versions, selectedVersionId, onSelect }: IndexVersionTableProps) {
  if (versions.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
        No index versions returned by FastAPI.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table className="min-w-[1120px]">
        <TableHeader>
          <TableRow>
            <TableHead>Version</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Docs</TableHead>
            <TableHead>Chunks</TableHead>
            <TableHead>Vectors</TableHead>
            <TableHead>Embedding</TableHead>
            <TableHead>Chunking</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Activated</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {versions.map((version) => (
            <TableRow
              className={`cursor-pointer transition hover:bg-slate-900/70 ${
                selectedVersionId === version.id ? "bg-cyan-950/20" : ""
              }`}
              key={version.id}
              onClick={() => onSelect(version.id)}
            >
              <TableCell>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-slate-100">{version.name}</span>
                  {version.is_active ? <Badge tone="good">Active</Badge> : null}
                </div>
                <div className="mt-1 font-mono text-xs text-slate-500">{shortId(version.id)}</div>
              </TableCell>
              <TableCell>
                <IndexStatusBadge status={version.status} />
              </TableCell>
              <TableCell className="font-mono">{formatCount(version.document_count)}</TableCell>
              <TableCell className="font-mono">{formatCount(version.chunk_count)}</TableCell>
              <TableCell className="font-mono">{formatCount(version.vector_count)}</TableCell>
              <TableCell>
                <div>{version.embedding_model || "Unavailable"}</div>
                <div className="mt-1 font-mono text-xs text-slate-500">{version.embedding_dimension ?? "dim unavailable"}</div>
              </TableCell>
              <TableCell>
                <div>{version.chunking_strategy || "Unavailable"}</div>
                <div className="mt-1 font-mono text-xs text-slate-500">{version.chunking_version || "version unavailable"}</div>
              </TableCell>
              <TableCell>{formatDate(version.created_at)}</TableCell>
              <TableCell>{formatDate(version.activated_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
