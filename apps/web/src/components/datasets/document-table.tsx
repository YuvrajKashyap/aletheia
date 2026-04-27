import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { DocumentListItem } from "@/lib/api/types";

function shortId(value?: string | null) {
  return value ? value.slice(0, 8) : "Unavailable";
}

export function DocumentTable({
  documents,
  onSelect
}: {
  documents: DocumentListItem[];
  onSelect: (documentId: string) => void;
}) {
  if (!documents.length) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">No documents found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>External ID</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Text preview</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((document) => (
            <TableRow key={document.id}>
              <TableCell className="font-mono text-xs">{document.external_id || shortId(document.id)}</TableCell>
              <TableCell className="min-w-48 text-slate-100">{document.title || "Untitled"}</TableCell>
              <TableCell className="min-w-96 max-w-xl text-slate-400">
                {document.text_preview || document.text || "Unavailable"}
              </TableCell>
              <TableCell className="whitespace-nowrap text-xs">{document.created_at || "Unavailable"}</TableCell>
              <TableCell>
                <Button variant="ghost" onClick={() => onSelect(document.id)}>
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
