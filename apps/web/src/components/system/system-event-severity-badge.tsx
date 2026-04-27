import { Badge } from "@/components/ui/badge";

export function SystemEventSeverityBadge({ severity }: { severity?: string | null }) {
  const value = severity?.toLowerCase() || "unknown";
  const tone = value === "error" ? "bad" : value === "warning" || value === "warn" ? "warn" : value === "info" ? "good" : "neutral";
  return <Badge tone={tone}>{value}</Badge>;
}
