export function formatCount(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? value.toLocaleString() : "Unavailable";
}

export function formatDate(value?: string | null): string {
  if (!value) {
    return "Unavailable";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function shortId(value?: string | null): string {
  if (!value) {
    return "Unavailable";
  }
  return value.length > 12 ? `${value.slice(0, 8)}...${value.slice(-4)}` : value;
}

export function progressPercent(completed?: number | null, total?: number | null): number | null {
  if (!total || total <= 0 || completed === null || completed === undefined) {
    return null;
  }
  return Math.max(0, Math.min(100, (completed / total) * 100));
}
