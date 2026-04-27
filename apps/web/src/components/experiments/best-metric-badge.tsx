import { Badge } from "@/components/ui/badge";

type BestMetricBadgeProps = {
  label: string;
};

export function BestMetricBadge({ label }: BestMetricBadgeProps) {
  return <Badge tone={label === "Fastest" ? "warn" : "good"}>{label}</Badge>;
}
