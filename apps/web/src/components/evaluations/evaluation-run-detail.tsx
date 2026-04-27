import { EvaluationMetricCards } from "@/components/evaluations/evaluation-metric-cards";
import { EvaluationQueryResultsTable } from "@/components/evaluations/evaluation-query-results-table";
import { EvaluationReportPanel } from "@/components/evaluations/evaluation-report-panel";
import { EvaluationStatusBadge } from "@/components/evaluations/evaluation-status-badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { EvaluationQueryResultItem, EvaluationReportResponse, EvaluationRunDetail } from "@/lib/api/types";

type RunDetailProps = {
  run: EvaluationRunDetail;
  results: EvaluationQueryResultItem[];
  report: EvaluationReportResponse | null;
  reportError?: string | null;
};

function valueOrUnavailable(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Unavailable";
  }
  return String(value);
}

export function EvaluationRunDetailPanel({ run, results, report, reportError }: RunDetailProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center gap-2">
            <EvaluationStatusBadge status={run.status} />
            <CardTitle>{run.name}</CardTitle>
          </div>
          <CardDescription>{run.notes || "No notes stored for this evaluation run."}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
            <Metadata label="run id" value={run.id} />
            <Metadata label="dataset id" value={run.dataset_id} />
            <Metadata label="index version id" value={run.index_version_id} />
            <Metadata label="experiment config id" value={run.experiment_config_id} />
          </div>
          <div>
            <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">config_json</div>
            <pre className="max-h-72 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
              {JSON.stringify(run.config_json || {}, null, 2)}
            </pre>
          </div>
        </CardContent>
      </Card>
      <EvaluationMetricCards run={run} />
      <Card>
        <CardHeader>
          <CardTitle>Per-query results</CardTitle>
          <CardDescription>First 50 query results for the selected evaluation run.</CardDescription>
        </CardHeader>
        <CardContent>
          <EvaluationQueryResultsTable results={results} />
        </CardContent>
      </Card>
      <EvaluationReportPanel report={report} errorMessage={reportError} />
    </div>
  );
}

function Metadata({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 select-all break-all font-mono text-xs text-slate-200">{valueOrUnavailable(value)}</div>
    </div>
  );
}
