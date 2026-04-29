import { apiFetch } from "@/lib/api/client";
import { getSnapshotExperimentConfigs } from "@/lib/api/snapshot";
import { isSnapshotMode } from "@/lib/demo-mode";
import type {
  ExperimentConfigListResponse,
  JobStatusResponse,
  SearchMode,
  SeedExperimentConfigsResponse,
  StartComparisonRequest,
  StartComparisonResponse
} from "@/lib/api/types";

type ExperimentConfigParams = {
  retrievalMode?: SearchMode | "all";
  isDefault?: boolean | null;
  limit?: number;
  offset?: number;
};

function queryString(params: Record<string, string | number | boolean | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

function adminHeaders(adminApiKey: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Admin-API-Key": adminApiKey
  };
}

export function getExperimentConfigs(params: ExperimentConfigParams = {}): Promise<ExperimentConfigListResponse> {
  if (isSnapshotMode()) {
    return getSnapshotExperimentConfigs(params);
  }

  return apiFetch<ExperimentConfigListResponse>(
    `/api/v1/experiments/configs${queryString({
      retrieval_mode: params.retrievalMode && params.retrievalMode !== "all" ? params.retrievalMode : undefined,
      is_default: params.isDefault === null ? undefined : params.isDefault,
      limit: params.limit ?? 50,
      offset: params.offset ?? 0
    })}`
  );
}

export function seedDefaultExperimentConfigs(adminApiKey: string): Promise<SeedExperimentConfigsResponse> {
  if (isSnapshotMode()) {
    throw new Error("Admin comparison jobs are disabled in public snapshot mode. Run the full local stack to launch new comparisons.");
  }

  return apiFetch<SeedExperimentConfigsResponse>("/api/v1/experiments/configs/seed-defaults", {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify({})
  });
}

export function startComparisonJob(
  request: StartComparisonRequest,
  adminApiKey: string
): Promise<StartComparisonResponse> {
  if (isSnapshotMode()) {
    throw new Error("Admin comparison jobs are disabled in public snapshot mode. Run the full local stack to launch new comparisons.");
  }

  return apiFetch<StartComparisonResponse>("/api/v1/experiments/comparisons", {
    method: "POST",
    headers: adminHeaders(adminApiKey),
    body: JSON.stringify(request)
  });
}

export function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  if (isSnapshotMode()) {
    throw new Error("Job status is unavailable in public snapshot mode because background workers are not hosted.");
  }

  return apiFetch<JobStatusResponse>(`/api/v1/system/jobs/${encodeURIComponent(jobId)}`);
}
