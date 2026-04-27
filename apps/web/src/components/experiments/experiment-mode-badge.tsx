import { Badge } from "@/components/ui/badge";
import { getModeLabel } from "@/components/experiments/experiment-data";

type ExperimentModeBadgeProps = {
  mode?: string | null;
};

export function ExperimentModeBadge({ mode }: ExperimentModeBadgeProps) {
  return <Badge tone="neutral">{getModeLabel(mode)}</Badge>;
}
