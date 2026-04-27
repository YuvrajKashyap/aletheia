import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type RankingSummaryProps = {
  summary?: Record<string, unknown>;
};

function isScalar(value: unknown): boolean {
  return value === null || ["string", "number", "boolean"].includes(typeof value);
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "unavailable";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  return String(value);
}

export function TraceRankingSummary({ summary }: RankingSummaryProps) {
  const entries = Object.entries(summary || {});
  const scalarEntries = entries.filter(([, value]) => isScalar(value));
  const objectEntries = entries.filter(([, value]) => !isScalar(value));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Ranking summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {entries.length === 0 ? (
          <p className="text-sm text-slate-500">No ranking summary returned for this trace.</p>
        ) : (
          <>
            {scalarEntries.length > 0 ? (
              <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                {scalarEntries.map(([key, value]) => (
                  <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2" key={key}>
                    <div className="text-[11px] uppercase tracking-wide text-slate-500">{key}</div>
                    <div className="mt-1 font-mono text-sm text-slate-100">{formatValue(value)}</div>
                  </div>
                ))}
              </div>
            ) : null}
            {objectEntries.length > 0 ? (
              <div className="space-y-3">
                {objectEntries.map(([key, value]) => (
                  <div className="rounded-md border border-slate-800 bg-slate-950 p-3" key={key}>
                    <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">{key}</div>
                    <pre className="max-h-56 overflow-auto text-xs text-slate-300">{JSON.stringify(value, null, 2)}</pre>
                  </div>
                ))}
              </div>
            ) : null}
          </>
        )}
      </CardContent>
    </Card>
  );
}
