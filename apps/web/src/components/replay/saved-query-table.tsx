import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { SavedQueryItem } from "@/lib/api/types";

function metadataString(metadata: Record<string, unknown> | undefined, key: string) {
  const value = metadata?.[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : "Unavailable";
}

export function SavedQueryTable({
  queries,
  onSelect
}: {
  queries: SavedQueryItem[];
  onSelect: (query: SavedQueryItem) => void;
}) {
  if (!queries.length) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">No saved queries found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Source</TableHead>
            <TableHead>Query text</TableHead>
            <TableHead>Query external ID</TableHead>
            <TableHead>Qrels</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
              Action
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {queries.map((query) => (
            <TableRow key={query.id}>
              <TableCell className="min-w-48 text-slate-100">{query.name || "Unnamed query"}</TableCell>
              <TableCell>
                <Badge tone="neutral">{query.source}</Badge>
              </TableCell>
              <TableCell className="min-w-96 max-w-xl text-slate-400">{query.text}</TableCell>
              <TableCell className="font-mono text-xs">{metadataString(query.metadata_json, "query_external_id")}</TableCell>
              <TableCell>{metadataString(query.metadata_json, "relevance_count")}</TableCell>
              <TableCell className="whitespace-nowrap text-xs">{query.created_at || "Unavailable"}</TableCell>
              <TableCell className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
                <Button variant="secondary" onClick={() => onSelect(query)}>
                  Select
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
