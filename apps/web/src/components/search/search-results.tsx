import { ResultCard } from "@/components/search/result-card";
import type { SearchResponse } from "@/lib/api/types";

type SearchResultsProps = {
  response: SearchResponse;
};

export function SearchResults({ response }: SearchResultsProps) {
  if (response.results.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-6 text-sm text-slate-400">
        The backend returned zero retrieval results for this query.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {response.results.map((result) => (
        <ResultCard key={`${result.rank}-${result.chunk_id}`} result={result} />
      ))}
    </div>
  );
}
