import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { BenchmarkQueryListItem } from "@/lib/api/types";

export function BenchmarkQueryTable({
  queries,
  onSelect
}: {
  queries: BenchmarkQueryListItem[];
  onSelect: (queryId: string) => void;
}) {
  if (!queries.length) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">No benchmark queries found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>External ID</TableHead>
            <TableHead>Split</TableHead>
            <TableHead>Query text</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
              Action
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {queries.map((query) => (
            <TableRow key={query.id}>
              <TableCell className="font-mono text-xs">{query.external_id}</TableCell>
              <TableCell>
                <Badge tone="neutral">{query.split || "unknown"}</Badge>
              </TableCell>
              <TableCell className="min-w-96 text-slate-300">{query.text}</TableCell>
              <TableCell className="whitespace-nowrap text-xs">{query.created_at || "Unavailable"}</TableCell>
              <TableCell className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
                <Button variant="secondary" onClick={() => onSelect(query.id)}>
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
