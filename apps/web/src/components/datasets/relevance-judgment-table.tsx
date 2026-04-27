import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { RelevanceJudgmentItem } from "@/lib/api/types";

function shortId(value?: string | null) {
  return value ? value.slice(0, 8) : "Unavailable";
}

export function RelevanceJudgmentTable({ judgments }: { judgments: RelevanceJudgmentItem[] }) {
  if (!judgments.length) {
    return (
      <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">
        No relevance judgments found for the current filters.
        Exact query or document external ID filters may not match any qrels.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Query external ID</TableHead>
            <TableHead>Document external ID</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Query ID</TableHead>
            <TableHead>Document ID</TableHead>
            <TableHead>Query text</TableHead>
            <TableHead>Document title</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {judgments.map((judgment) => (
            <TableRow key={judgment.id}>
              <TableCell className="font-mono text-xs">{judgment.query_external_id || shortId(judgment.query_id)}</TableCell>
              <TableCell className="font-mono text-xs">
                {judgment.document_external_id || shortId(judgment.document_id)}
              </TableCell>
              <TableCell>{judgment.relevance_score ?? "Unavailable"}</TableCell>
              <TableCell className="font-mono text-xs">{shortId(judgment.query_id)}</TableCell>
              <TableCell className="font-mono text-xs">{shortId(judgment.document_id)}</TableCell>
              <TableCell className="min-w-80 max-w-lg text-slate-400">{judgment.query_text || "Unavailable"}</TableCell>
              <TableCell className="min-w-48 text-slate-300">{judgment.document_title || "Unavailable"}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
