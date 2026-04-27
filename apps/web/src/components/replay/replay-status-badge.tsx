import { Badge } from "@/components/ui/badge";

export function ReplayStatusBadge({ status }: { status?: string | null }) {
  const normalized = (status || "unknown").toLowerCase();
  const tone =
    normalized === "completed" || normalized === "finished"
      ? "good"
      : normalized === "failed" || normalized === "error"
        ? "bad"
        : normalized === "running" || normalized === "started" || normalized === "queued" || normalized === "pending"
          ? "warn"
          : "neutral";

  return <Badge tone={tone}>{normalized}</Badge>;
}
