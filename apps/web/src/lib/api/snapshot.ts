type SnapshotFileName =
  | "manifest.json"
  | "overview.json"
  | "index-status.json"
  | "datasets.json"
  | "documents-sample.json"
  | "chunks-sample.json"
  | "benchmark-queries-sample.json"
  | "relevance-judgments-sample.json"
  | "search-scenarios.json"
  | "traces.json"
  | "evaluations.json"
  | "experiments.json"
  | "replay.json"
  | "system.json";

function snapshotUrl(fileName: string): string {
  const path = `/demo-data/${fileName}`;
  if (typeof window !== "undefined") {
    return path;
  }

  const configured = process.env.NEXT_PUBLIC_SITE_URL;
  if (configured) {
    return `${configured.replace(/\/+$/, "")}${path}`;
  }

  const vercelUrl = process.env.VERCEL_URL;
  if (vercelUrl) {
    return `https://${vercelUrl.replace(/\/+$/, "")}${path}`;
  }

  return `http://localhost:3000${path}`;
}

export async function fetchSnapshotFile<T>(fileName: SnapshotFileName): Promise<T> {
  const response = await fetch(snapshotUrl(fileName), {
    cache: "no-store",
    headers: {
      Accept: "application/json"
    }
  });

  if (!response.ok) {
    throw new Error(`Snapshot file ${fileName} is unavailable with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getSnapshotManifest() {
  return fetchSnapshotFile<Record<string, unknown>>("manifest.json");
}

export function getSnapshotOverview() {
  return fetchSnapshotFile<Record<string, unknown>>("overview.json");
}

export function getSnapshotIndexStatus() {
  return fetchSnapshotFile<Record<string, unknown>>("index-status.json");
}

export function getSnapshotDatasets() {
  return fetchSnapshotFile<Record<string, unknown>>("datasets.json");
}

export function getSnapshotSearchScenarios() {
  return fetchSnapshotFile<Record<string, unknown>>("search-scenarios.json");
}

export function getSnapshotTraces() {
  return fetchSnapshotFile<Record<string, unknown>>("traces.json");
}

export function getSnapshotEvaluations() {
  return fetchSnapshotFile<Record<string, unknown>>("evaluations.json");
}

export function getSnapshotExperiments() {
  return fetchSnapshotFile<Record<string, unknown>>("experiments.json");
}

export function getSnapshotReplay() {
  return fetchSnapshotFile<Record<string, unknown>>("replay.json");
}

export function getSnapshotSystem() {
  return fetchSnapshotFile<Record<string, unknown>>("system.json");
}
