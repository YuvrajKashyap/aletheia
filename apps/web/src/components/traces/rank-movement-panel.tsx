import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type RankMovementPanelProps = {
  rankingSummary?: Record<string, unknown>;
};

function numberField(summary: Record<string, unknown>, key: string): number | null {
  const value = summary[key];
  return typeof value === "number" ? value : null;
}

function asMovementRows(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item && typeof item === "object")) : [];
}

function field(row: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const value = row[key];
    if (value !== null && value !== undefined && value !== "") {
      return String(value);
    }
  }
  return "";
}

export function RankMovementPanel({ rankingSummary }: RankMovementPanelProps) {
  const summary = rankingSummary || {};
  const movedUp = numberField(summary, "moved_up");
  const movedDown = numberField(summary, "moved_down");
  const unchanged = numberField(summary, "unchanged");
  const largestUpwardMove = numberField(summary, "largest_upward_move");
  const largestDownwardMove = numberField(summary, "largest_downward_move");
  const rows = asMovementRows(summary.movements);

  if ([movedUp, movedDown, unchanged, largestUpwardMove, largestDownwardMove].every((value) => value === null) && rows.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Rank movement</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">No rank movement data available for this trace.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rank movement</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-5">
          <Metric label="moved up" value={movedUp} />
          <Metric label="moved down" value={movedDown} />
          <Metric label="unchanged" value={unchanged} />
          <Metric label="largest upward" value={largestUpwardMove} />
          <Metric label="largest downward" value={largestDownwardMove} />
        </div>
        {rows.length > 0 ? (
          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="min-w-[720px] w-full text-left text-sm">
              <thead className="border-b border-slate-800 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">fusion rank</th>
                  <th className="px-3 py-2">rerank rank</th>
                  <th className="px-3 py-2">movement</th>
                  <th className="px-3 py-2">reranker score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900">
                {rows.map((row, index) => (
                  <tr key={`${field(row, ["chunk_id", "document_id", "id"])}-${index}`}>
                    <td className="px-3 py-2 font-mono text-slate-300">{field(row, ["document_id", "chunk_id", "id"])}</td>
                    <td className="px-3 py-2 font-mono text-slate-300">{field(row, ["fusion_rank", "source_rank", "original_rank"])}</td>
                    <td className="px-3 py-2 font-mono text-slate-300">{field(row, ["rerank_rank", "target_rank", "final_rank"])}</td>
                    <td className="px-3 py-2 font-mono text-slate-300">{field(row, ["movement"])}</td>
                    <td className="px-3 py-2 font-mono text-slate-300">{field(row, ["reranker_score"])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 font-mono text-sm text-slate-100">{value === null ? "unavailable" : value}</div>
    </div>
  );
}
