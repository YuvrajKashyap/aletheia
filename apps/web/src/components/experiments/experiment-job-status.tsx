"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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

  return (
    <Card className="border-slate-800 bg-slate-950/70">
      <CardHeader>
        <CardTitle>Comparison job</CardTitle>
        <CardDescription>Job status comes from the FastAPI system job endpoint.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid gap-2 text-sm md:grid-cols-3">
          <JobField label="Job ID" value={startedJob.job_id} />
          <JobField label="Queue" value={startedJob.queue || "Unavailable"} />
          <JobField label="Submit status" value={startedJob.status || "Unavailable"} />
        </div>
        <Button disabled={isLoading} type="button" onClick={onRefresh}>
          {isLoading ? "Refreshing" : "Refresh job"}
        </Button>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        {jobStatus ? (
          <pre className="max-h-80 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
            {JSON.stringify(jobStatus, null, 2)}
          </pre>
        ) : null}
      </CardContent>
    </Card>
  );
}

function JobField({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 break-all font-mono text-xs text-slate-200">{value}</div>
    </div>
  );
}
