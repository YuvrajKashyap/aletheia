import { Badge } from "@/components/ui/badge";

type TraceStatusBadgeProps = {
  status: string;
};

export function TraceStatusBadge({ status }: TraceStatusBadgeProps) {
  const normalized = status.toLowerCase();
  const tone = normalized === "completed" ? "good" : normalized === "failed" ? "bad" : normalized === "running" ? "warn" : "neutral";

  return <Badge tone={tone}>{status}</Badge>;
}
