import type { OperationalStatus } from "@/components/system/operational-status-badge";
import type { WorkerHeartbeatItem } from "@/lib/api/types";

const RECENT_HEARTBEAT_MS = 60_000;

const LIVE_WORKER_STATUSES = new Set(["running", "healthy", "idle", "working", "busy", "started"]);
const ERROR_WORKER_STATUSES = new Set(["error", "failed", "stopped", "dead", "unhealthy"]);

export function workerTimestamp(worker: WorkerHeartbeatItem): string | null {
  return worker.last_seen_at || worker.updated_at || worker.created_at || null;
}

export function workerHeartbeatAgeMs(worker: WorkerHeartbeatItem, now = Date.now()): number | null {
  const timestamp = workerTimestamp(worker);
  if (!timestamp) return null;
  const time = new Date(timestamp).getTime();
  return Number.isFinite(time) ? Math.max(0, now - time) : null;
}

export function isWorkerHeartbeatRecent(worker: WorkerHeartbeatItem, now = Date.now()): boolean {
  const ageMs = workerHeartbeatAgeMs(worker, now);
  return ageMs !== null && ageMs <= RECENT_HEARTBEAT_MS;
}

export function workerOperationalStatus(worker: WorkerHeartbeatItem | null, endpointError?: string | null): OperationalStatus {
  if (endpointError) return "error";
  if (!worker) return "warning";

  const status = worker.status?.toLowerCase();
  if (ERROR_WORKER_STATUSES.has(status)) return "error";
  if (LIVE_WORKER_STATUSES.has(status)) {
    return isWorkerHeartbeatRecent(worker) ? "healthy" : "warning";
  }
  return "warning";
}
