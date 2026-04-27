import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function listFromComparison(comparison: Record<string, unknown> | undefined, keys: string[]) {
  for (const key of keys) {
    const value = comparison?.[key];
    if (Array.isArray(value)) {
      return value.map((item) => String(item));
    }
  }
  return [];
}

export function ReplayDocumentLists({ comparison }: { comparison?: Record<string, unknown> }) {
  const ranked = listFromComparison(comparison, ["ranked_document_ids"]);
  const relevant = listFromComparison(comparison, ["relevant_document_ids"]);
  const matched = listFromComparison(comparison, ["matched_relevant_document_ids"]);
  const missed = listFromComparison(comparison, ["missed_relevant_document_ids"]);

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <DocumentList title="Matched relevant documents" description="Relevant document IDs found by this replay." values={matched} />
      <DocumentList title="Missed relevant documents" description="Relevant document IDs not found by this replay." values={missed} />
      <DocumentList title="Ranked document IDs" description="Deduplicated ranked documents from the target trace." values={ranked} />
      <DocumentList title="Relevant document IDs" description="Qrels-backed relevant documents when available." values={relevant} />
    </div>
  );
}

function DocumentList({ title, description, values }: { title: string; description: string; values: string[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        {values.length ? (
          <div className="flex max-h-40 flex-wrap gap-2 overflow-auto">
            {values.map((value) => (
              <span key={value} className="rounded border border-slate-800 bg-slate-950 px-2 py-1 font-mono text-xs text-slate-300">
                {value}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400">Unavailable</p>
        )}
      </CardContent>
    </Card>
  );
}
