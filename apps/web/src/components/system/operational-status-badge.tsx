import { Badge } from "@/components/ui/badge";

export type OperationalStatus = "healthy" | "warning" | "error" | "unknown";

export function OperationalStatusBadge({ status }: { status: OperationalStatus | string | undefined }) {
  const normalized = normalizeStatus(status);
  return (
    <Badge tone={normalized === "healthy" ? "good" : normalized === "warning" ? "warn" : normalized === "error" ? "bad" : "neutral"}>
      {normalized}
    </Badge>
  );
}

export function normalizeStatus(status: OperationalStatus | string | undefined): OperationalStatus {
  const value = status?.toLowerCase();
  if (value === "healthy" || value === "ok" || value === "reachable" || value === "running" || value === "loaded") {
    return "healthy";
  }
  if (value === "warning" || value === "queued" || value === "pending" || value === "not_loaded") {
    return "warning";
  }
  if (value === "error" || value === "failed" || value === "unhealthy" || value === "unreachable") {
    return "error";
  }
  return "unknown";
}
