"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { EvaluationReportResponse } from "@/lib/api/types";

type ReportPanelProps = {
  report: EvaluationReportResponse | null;
  errorMessage?: string | null;
};

export function EvaluationReportPanel({ report, errorMessage }: ReportPanelProps) {
  const [showFullReport, setShowFullReport] = useState(false);

  if (errorMessage) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Evaluation report</CardTitle>
          <CardDescription>Report unavailable.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-400">{errorMessage}</p>
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Evaluation report</CardTitle>
          <CardDescription>No report loaded for the selected run.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <div>
          <CardTitle>Evaluation report</CardTitle>
          <CardDescription>Stored report metadata and JSON from the backend.</CardDescription>
        </div>
        {report.report_json ? (
          <Button type="button" variant="ghost" onClick={() => setShowFullReport((current) => !current)}>
            {showFullReport ? "Hide report JSON" : "Show report JSON"}
          </Button>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-2 md:grid-cols-2">
          <Metadata label="report_path" value={report.report_path} />
          <Metadata label="report_format" value={report.report_format} />
        </div>
        {report.warning ? <p className="text-sm text-amber-300">{report.warning}</p> : null}
        <div>
          <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">summary_json</div>
          <pre className="max-h-72 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
            {JSON.stringify(report.summary_json || {}, null, 2)}
          </pre>
        </div>
        {showFullReport && report.report_json ? (
          <div>
            <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">report_json</div>
            <pre className="max-h-[520px] overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
              {JSON.stringify(report.report_json, null, 2)}
            </pre>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Metadata({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 select-all break-all font-mono text-xs text-slate-200">{value || "Unavailable"}</div>
    </div>
  );
}
