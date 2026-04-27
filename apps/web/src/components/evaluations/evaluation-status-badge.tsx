import { Badge } from "@/components/ui/badge";

type EvaluationStatusBadgeProps = {
  status: string;
};

export function EvaluationStatusBadge({ status }: EvaluationStatusBadgeProps) {
  const normalized = status.toLowerCase();
  const tone = normalized === "completed" ? "good" : normalized === "failed" ? "bad" : normalized === "running" ? "warn" : "neutral";

  return <Badge tone={tone}>{status}</Badge>;
}
