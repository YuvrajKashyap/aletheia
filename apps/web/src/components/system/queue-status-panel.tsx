import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { OperationalStatusBadge } from "@/components/system/operational-status-badge";
import type { QueueStatusResponse } from "@/lib/api/types";

export function QueueStatusPanel({
  queue,
  error,
  snapshotMode = false
}: {
  queue: QueueStatusResponse | null;
  error?: string | null;
  snapshotMode?: boolean;
}) {
  if (snapshotMode) {
    return (
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <CardTitle>Queue status</CardTitle>
            <OperationalStatusBadge status="warning" />
          </div>
          <CardDescription>Redis/RQ is local-only in public snapshot mode.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm md:grid-cols-3">
          <Field label="Queue" value="local full stack only" />
          <Field label="Public jobs" value="disabled" />
          <Field label="Status" value="Public snapshot mode does not run Redis/RQ." />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle>Queue status</CardTitle>
          <OperationalStatusBadge status={error ? "error" : queue ? "healthy" : "unknown"} />
        </div>
        <CardDescription>Redis and RQ queue reachability.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3 text-sm md:grid-cols-3">
        <Field label="Queue" value={queue?.queue} />
        <Field label="Job count" value={queue?.job_count} />
        <Field label="Status" value={error || queue?.status || (queue ? "reachable" : undefined)} tone={error ? "error" : "normal"} />
      </CardContent>
    </Card>
  );
}

function Field({ label, value, tone = "normal" }: { label: string; value?: string | number | null; tone?: "normal" | "error" }) {
  return (
    <div>
      <div className="text-slate-500">{label}</div>
      <div className={tone === "error" ? "break-all text-red-300" : "break-all text-slate-200"}>{value ?? "Unavailable"}</div>
    </div>
  );
}
