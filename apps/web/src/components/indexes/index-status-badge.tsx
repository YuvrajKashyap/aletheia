import { Badge } from "@/components/ui/badge";

type IndexStatusBadgeProps = {
  status?: string | null;
};

export function IndexStatusBadge({ status }: IndexStatusBadgeProps) {
  const normalized = (status || "unknown").toLowerCase();
  const tone =
    normalized === "active" || normalized === "ready" || normalized === "completed"
      ? "good"
      : normalized === "failed"
        ? "bad"
        : normalized === "building" || normalized === "running" || normalized === "queued"
          ? "warn"
          : "neutral";

  return <Badge tone={tone}>{status || "Unknown"}</Badge>;
}
