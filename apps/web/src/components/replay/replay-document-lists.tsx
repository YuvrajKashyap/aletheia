import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type DocumentListState = {
  values: string[];
  isAvailable: boolean;
};

function nestedObject(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : undefined;
}

function valueAtPath(comparison: Record<string, unknown> | undefined, path: string[]) {
  let current: unknown = comparison;
  for (const key of path) {
    const object = nestedObject(current);
    if (!object) return undefined;
    current = object[key];
  }
  return current;
}

function listFromComparison(comparison: Record<string, unknown> | undefined, paths: string[][]): DocumentListState {
  for (const path of paths) {
    const value = valueAtPath(comparison, path);
    if (Array.isArray(value)) {
      return {
        values: value.map((item) => String(item)),
        isAvailable: true,
      };
    }
  }
  return { values: [], isAvailable: false };
}

export function ReplayDocumentLists({ comparison }: { comparison?: Record<string, unknown> }) {
  const ranked = listFromComparison(comparison, [["ranked_document_ids"], ["metrics", "ranked_document_ids"]]);
  const relevant = listFromComparison(comparison, [["relevant_document_ids"], ["metrics", "relevant_document_ids"]]);
  const matched = listFromComparison(comparison, [["matched_relevant_document_ids"], ["metrics", "matched_relevant_document_ids"]]);
  const missed = listFromComparison(comparison, [["missed_relevant_document_ids"], ["metrics", "missed_relevant_document_ids"]]);

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <DocumentList
        title="Matched relevant documents"
        description="Relevant document IDs found by this replay."
        emptyText="No matched relevant documents."
        list={matched}
      />
      <DocumentList
        title="Missed relevant documents"
        description="Relevant document IDs not found by this replay."
        emptyText="No missed relevant documents."
        list={missed}
      />
      <DocumentList
        title="Ranked document IDs"
        description="Deduplicated ranked documents from the target trace."
        emptyText="No ranked documents."
        list={ranked}
      />
      <DocumentList
        title="Relevant document IDs"
        description="Qrels-backed relevant documents when available."
        emptyText="No relevant documents."
        list={relevant}
      />
    </div>
  );
}

function DocumentList({
  title,
  description,
  emptyText,
  list,
}: {
  title: string;
  description: string;
  emptyText: string;
  list: DocumentListState;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        {list.values.length ? (
          <div className="flex max-h-40 flex-wrap gap-2 overflow-auto">
            {list.values.map((value) => (
              <span key={value} className="rounded border border-slate-800 bg-slate-950 px-2 py-1 font-mono text-xs text-slate-300">
                {value}
              </span>
            ))}
          </div>
        ) : list.isAvailable ? (
          <p className="text-sm text-slate-400">{emptyText}</p>
        ) : (
          <p className="text-sm text-slate-400">Unavailable</p>
        )}
      </CardContent>
    </Card>
  );
}
