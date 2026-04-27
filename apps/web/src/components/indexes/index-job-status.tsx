import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { IndexStatusBadge } from "@/components/indexes/index-status-badge";
import type { BuildIndexJobResponse, JobStatusResponse } from "@/lib/api/types";

type IndexJobStatusProps = {
  buildJob: BuildIndexJobResponse | null;
  jobStatus: JobStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
};

export function IndexJobStatus({ buildJob, jobStatus, isLoading, error, onRefresh }: IndexJobStatusProps) {
  if (!buildJob) {
    return null;
  }

  return (
    <Card className="border-slate-800 bg-slate-950/70">
      <CardHeader>
        <CardTitle>Build job</CardTitle>
        <CardDescription>Queued build job and current RQ status.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {jobStatus?.status ? (
          <div className="flex flex-wrap items-center gap-2 rounded-md border border-slate-800 bg-slate-950 p-3">
            <span className="text-xs uppercase tracking-wide text-slate-500">Current status</span>
            <IndexStatusBadge status={jobStatus.status} />
          </div>
        ) : null}
        <div className="grid gap-2 md:grid-cols-3">
          <Field label="Job ID" value={buildJob.job_id} />
          <Field label="Queue" value={buildJob.queue || "Unavailable"} />
          <Field label="Initial status" value={buildJob.status || "Unavailable"} />
        </div>
        <Button disabled={isLoading} type="button" onClick={onRefresh}>
          {isLoading ? "Refreshing" : "Refresh job"}
        </Button>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        {jobStatus ? (
          <pre className="max-h-72 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
            {JSON.stringify(jobStatus, null, 2)}
          </pre>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 break-all font-mono text-xs text-slate-200">{value}</div>
    </div>
  );
}
