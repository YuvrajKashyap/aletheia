import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { OperationalStatusBadge } from "@/components/system/operational-status-badge";
import { workerHeartbeatAgeMs, workerOperationalStatus, workerTimestamp } from "@/components/system/worker-status";
import type { WorkerHeartbeatItem } from "@/lib/api/types";

function shortId(value?: string | null) {
  return value ? value.slice(0, 12) : "Unavailable";
}

function ageSince(worker: WorkerHeartbeatItem) {
  const ageMs = workerHeartbeatAgeMs(worker);
  if (ageMs === null) return "Unavailable";
  const seconds = Math.floor(ageMs / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h`;
}

export function WorkerHeartbeatPanel({ workers, error }: { workers: WorkerHeartbeatItem[]; error?: string | null }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Worker heartbeats</CardTitle>
        <CardDescription>Worker liveness from backend heartbeat rows.</CardDescription>
      </CardHeader>
      <CardContent>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        {!error && !workers.length ? <p className="text-sm text-amber-300">No recent worker heartbeat.</p> : null}
        {workers.length ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Worker</TableHead>
                  <TableHead>Queue</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Current job</TableHead>
                  <TableHead>Last seen</TableHead>
                  <TableHead>Age</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {workers.map((worker) => (
                  <TableRow key={worker.worker_name}>
                    <TableCell className="font-mono text-xs">{worker.worker_name}</TableCell>
                    <TableCell>{worker.queue_name || "Unavailable"}</TableCell>
                    <TableCell>
                      <OperationalStatusBadge status={workerOperationalStatus(worker)} />
                    </TableCell>
                    <TableCell className="font-mono text-xs">{shortId(worker.current_job_id)}</TableCell>
                    <TableCell className="font-mono text-xs">{workerTimestamp(worker) || "Unavailable"}</TableCell>
                    <TableCell>{ageSince(worker)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
