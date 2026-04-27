import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { TraceCandidateItem } from "@/lib/api/types";

type CandidateTableProps = {
  candidates: TraceCandidateItem[];
  candidatesBySource?: Record<string, TraceCandidateItem[]>;
};

function groupCandidates(
  candidates: TraceCandidateItem[],
  candidatesBySource?: Record<string, TraceCandidateItem[]>
): Record<string, TraceCandidateItem[]> {
  if (candidatesBySource && Object.keys(candidatesBySource).length > 0) {
    return candidatesBySource;
  }

  return candidates.reduce<Record<string, TraceCandidateItem[]>>((groups, candidate) => {
    const source = candidate.source || "unknown";
    groups[source] = groups[source] || [];
    groups[source].push(candidate);
    return groups;
  }, {});
}

function shortId(value?: string | null): string {
  if (!value) {
    return "unavailable";
  }
  return value.length > 10 ? value.slice(0, 8) : value;
}

function formatNumber(value?: number | null): string {
  if (value === null || value === undefined) {
    return "";
  }
  return Number.isInteger(value) ? String(value) : value.toFixed(4);
}

function metadataTitle(metadata?: Record<string, unknown>): string {
  if (!metadata) {
    return "";
  }
  for (const key of ["title", "document_title", "doc_title", "external_id"]) {
    const value = metadata[key];
    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }
  return "";
}

export function TraceCandidateTable({ candidates, candidatesBySource }: CandidateTableProps) {
  const groups = groupCandidates(candidates, candidatesBySource);
  const entries = Object.entries(groups);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Candidate provenance</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {entries.length === 0 ? (
          <p className="text-sm text-slate-500">No candidates returned for this trace.</p>
        ) : (
          entries.map(([source, items]) => (
            <div key={source}>
              <div className="mb-2 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-100">{source}</h3>
                <span className="text-xs text-slate-500">{items.length} candidates</span>
              </div>
              <div className="overflow-x-auto rounded-lg border border-slate-800">
                <Table className="min-w-[980px]">
                  <TableHeader>
                    <TableRow>
                      <TableHead>final</TableHead>
                      <TableHead>bm25</TableHead>
                      <TableHead>dense</TableHead>
                      <TableHead>fusion</TableHead>
                      <TableHead>rerank</TableHead>
                      <TableHead>bm25 score</TableHead>
                      <TableHead>dense score</TableHead>
                      <TableHead>fusion score</TableHead>
                      <TableHead>reranker score</TableHead>
                      <TableHead>chunk</TableHead>
                      <TableHead>document</TableHead>
                      <TableHead>title</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((candidate, index) => (
                      <TableRow key={candidate.id || `${source}-${candidate.chunk_id}-${index}`}>
                        <TableCell className="font-mono">{formatNumber(candidate.final_rank)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.bm25_rank)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.dense_rank)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.fusion_rank)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.rerank_rank)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.bm25_score)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.dense_score)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.fusion_score)}</TableCell>
                        <TableCell className="font-mono">{formatNumber(candidate.reranker_score)}</TableCell>
                        <TableCell className="select-all font-mono">{shortId(candidate.chunk_id)}</TableCell>
                        <TableCell className="select-all font-mono">{shortId(candidate.document_id)}</TableCell>
                        <TableCell className="max-w-64 truncate">{metadataTitle(candidate.metadata_json)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
