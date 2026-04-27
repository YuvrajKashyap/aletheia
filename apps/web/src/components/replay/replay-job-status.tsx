import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ReplayStatusBadge } from "@/components/replay/replay-status-badge";
import type { JobStatusResponse, ReplayResponse } from "@/lib/api/types";

export function ReplayJobStatus({
  response,
  jobStatus,
  isLoading,
  error,
  onRefresh
}: {
  response: ReplayResponse | null;
  jobStatus: JobStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
}) {
  if (!response?.job_id) {
    return null;
  }

  const result = jobStatus?.result;
  const resultObject = result && typeof result === "object" ? (result as Record<string, unknown>) : undefined;
  const replayIds = Array.isArray(resultObject?.replay_ids) ? resultObject.replay_ids.length : undefined;
  const reportPath = typeof resultObject?.report_path === "string" ? resultObject.report_path : undefined;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Replay job</CardTitle>
        <CardDescription>Current status comes from the FastAPI system job endpoint.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {jobStatus?.status ? (
          <div className="flex flex-wrap items-center gap-2 rounded-md border border-slate-800 bg-slate-950 p-3">
            <span className="text-xs uppercase tracking-wide text-slate-500">Current status</span>
            <ReplayStatusBadge status={jobStatus.status} />
          </div>
        ) : null}
        <div className="grid gap-2 text-sm md:grid-cols-3">
          <Field label="Job ID" value={response.job_id} />
          <Field label="Queue" value={response.queue || "Unavailable"} />
          <Field label="Initial status" value={response.status || "Unavailable"} />
        </div>
        <Button disabled={isLoading} type="button" onClick={onRefresh}>
          {isLoading ? "Refreshing" : "Refresh job"}
        </Button>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        {reportPath ? <p className="text-sm text-slate-300">Report path: <span className="font-mono text-xs">{reportPath}</span></p> : null}
        {replayIds !== undefined ? <p className="text-sm text-slate-300">Replay IDs: {replayIds}</p> : null}
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
