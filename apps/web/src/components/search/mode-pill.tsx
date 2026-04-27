import { Badge } from "@/components/ui/badge";
import type { SearchMode } from "@/lib/api/types";
import { getSearchModeLabel } from "@/lib/api/search";

type ModePillProps = {
  mode: SearchMode;
};

export function ModePill({ mode }: ModePillProps) {
  const tone = mode === "hybrid_rerank" ? "warn" : mode === "hybrid" ? "good" : "neutral";

  return <Badge tone={tone}>{getSearchModeLabel(mode)}</Badge>;
}
