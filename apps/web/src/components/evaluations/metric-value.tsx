type MetricValueProps = {
  value?: number | null;
  kind?: "metric" | "latency" | "count";
};

export function formatMetricValue(value?: number | null, kind: "metric" | "latency" | "count" = "metric"): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "Unavailable";
  }
  if (kind === "latency") {
    return `${value.toFixed(1)} ms`;
  }
  if (kind === "count") {
    return String(value);
  }
  return value.toFixed(4);
}

export function MetricValue({ value, kind = "metric" }: MetricValueProps) {
  return <span>{formatMetricValue(value, kind)}</span>;
}
