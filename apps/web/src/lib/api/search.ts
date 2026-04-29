import { apiFetch } from "@/lib/api/client";
import { runSnapshotSearch } from "@/lib/api/snapshot";
import { isSnapshotMode } from "@/lib/demo-mode";
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
  if (isSnapshotMode()) {
    return runSnapshotSearch(request);
  }

  return apiFetch<SearchResponse>("/api/v1/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });
}
