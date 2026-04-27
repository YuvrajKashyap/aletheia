import { apiFetch } from "@/lib/api/client";
import type { SearchMode, SearchRequest, SearchResponse } from "@/lib/api/types";

export function getSearchModeLabel(mode: SearchMode): string {
  const labels: Record<SearchMode, string> = {
    bm25: "BM25",
    dense: "Dense",
    hybrid: "Hybrid RRF",
    hybrid_rerank: "Hybrid Rerank"
  };

  return labels[mode];
}

export async function runSearch(request: SearchRequest): Promise<SearchResponse> {
  return apiFetch<SearchResponse>("/api/v1/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });
}
