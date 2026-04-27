"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { JobStatusResponse, StartComparisonResponse } from "@/lib/api/types";

type ExperimentJobStatusProps = {
  startedJob: StartComparisonResponse | null;
  jobStatus: JobStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
};

export function ExperimentJobStatus({
  startedJob,
  jobStatus,
  isLoading,
  error,
  onRefresh
}: ExperimentJobStatusProps) {
  if (!startedJob) {
    return null;
  }

  const currentStatus = jobStatus?.status;
  const statusTone = currentStatus === "finished" ? "good" : currentStatus === "failed" ? "bad" : "warn";

  return (
    <Card className="border-slate-800 bg-slate-950/70">
      <CardHeader>
        <CardTitle>Comparison job</CardTitle>
        <CardDescription>Job status comes from the FastAPI system job endpoint.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {currentStatus ? (
          <div className="rounded-md border border-slate-800 bg-slate-950 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs uppercase tracking-wide text-slate-500">Current status</span>
              <Badge tone={statusTone}>{currentStatus}</Badge>
            </div>
            {currentStatus === "finished" ? (
              <p className="mt-2 text-sm text-slate-400">Refresh the matrix to load new evaluation runs.</p>
            ) : null}
            {jobStatus.error ? <p className="mt-2 text-sm text-red-300">{jobStatus.error}</p> : null}
          </div>
        ) : null}
        <div className="grid gap-2 text-sm md:grid-cols-3">
          <JobField label="Job ID" value={startedJob.job_id} />
          <JobField label="Queue" value={startedJob.queue || "Unavailable"} />
          <JobField label="Initial submit status" value={startedJob.status || "Unavailable"} muted={Boolean(currentStatus)} />
        </div>
        <Button disabled={isLoading} type="button" onClick={onRefresh}>
          {isLoading ? "Refreshing" : "Refresh job"}
        </Button>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        {jobStatus?.result !== undefined ? (
          <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
            <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">Job result</div>
            <pre className="max-h-72 overflow-auto text-xs text-slate-300">
              {typeof jobStatus.result === "string" ? jobStatus.result : JSON.stringify(jobStatus.result, null, 2)}
            </pre>
          </div>
        ) : null}
        {jobStatus ? (
          <pre className="max-h-80 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
            {JSON.stringify(jobStatus, null, 2)}
          </pre>
        ) : null}
      </CardContent>
    </Card>
  );
}

function JobField({ label, value, muted = false }: { label: string; value: string; muted?: boolean }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-1 break-all font-mono text-xs ${muted ? "text-slate-500" : "text-slate-200"}`}>{value}</div>
    </div>
  );
}
