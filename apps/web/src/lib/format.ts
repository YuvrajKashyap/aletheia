export function formatUnavailable(value = "Unavailable"): string {
  return value;
}

export function safeString(value: unknown, fallback = "Unavailable"): string {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }
  if (typeof value === "boolean") {
    return String(value);
  }
  return fallback;
}

export function formatNumber(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? value.toLocaleString() : formatUnavailable();
}

export function formatMetric(value?: number | null, digits = 4): string {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : formatUnavailable();
}

export function formatLatency(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(1)} ms` : formatUnavailable();
}

export function formatDateTime(value?: string | null): string {
  if (!value) {
    return formatUnavailable();
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function formatShortId(value?: string | null, length = 8): string {
  return value ? value.slice(0, length) : formatUnavailable();
}
