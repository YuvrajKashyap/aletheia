import { apiFetch } from "@/lib/api/client";
import {
  getSnapshotEvaluationRun,
  getSnapshotEvaluationRunReport,
  getSnapshotEvaluationRunResults,
  getSnapshotEvaluationRuns
} from "@/lib/api/snapshot";
import { isSnapshotMode } from "@/lib/demo-mode";
import type {
  EvaluationQueryResultListResponse,
  EvaluationReportResponse,
  EvaluationRunDetail,
  EvaluationRunListResponse
} from "@/lib/api/types";

type EvaluationRunParams = {
  status?: string | "all";
  limit?: number;
  offset?: number;
};

type EvaluationResultParams = {
  limit?: number;
  offset?: number;
  failedOnly?: boolean;
};

type EvaluationReportParams = {
  includeJson?: boolean;
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

export function getEvaluationRuns(params: EvaluationRunParams = {}): Promise<EvaluationRunListResponse> {
  if (isSnapshotMode()) {
    return getSnapshotEvaluationRuns(params);
  }

  return apiFetch<EvaluationRunListResponse>(
    `/api/v1/evaluations/runs${queryString({
      status: params.status && params.status !== "all" ? params.status : undefined,
      limit: params.limit ?? 25,
      offset: params.offset ?? 0
    })}`
  );
}

export function getEvaluationRun(runId: string): Promise<EvaluationRunDetail> {
  if (isSnapshotMode()) {
    return getSnapshotEvaluationRun(runId);
  }

  return apiFetch<EvaluationRunDetail>(`/api/v1/evaluations/runs/${encodeURIComponent(runId)}`);
}

export function getEvaluationRunResults(
  runId: string,
  params: EvaluationResultParams = {}
): Promise<EvaluationQueryResultListResponse> {
  if (isSnapshotMode()) {
    return getSnapshotEvaluationRunResults(runId, params);
  }

  return apiFetch<EvaluationQueryResultListResponse>(
    `/api/v1/evaluations/runs/${encodeURIComponent(runId)}/results${queryString({
      limit: params.limit ?? 50,
      offset: params.offset ?? 0,
      failed_only: params.failedOnly
    })}`
  );
}

export function getEvaluationRunReport(
  runId: string,
  params: EvaluationReportParams = {}
): Promise<EvaluationReportResponse> {
  if (isSnapshotMode()) {
    return getSnapshotEvaluationRunReport(runId);
  }

  return apiFetch<EvaluationReportResponse>(
    `/api/v1/evaluations/runs/${encodeURIComponent(runId)}/report${queryString({
      include_json: params.includeJson ?? true
    })}`
  );
}
