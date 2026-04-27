"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type TraceJsonPanelProps = {
  traceJson: Record<string, unknown>;
  rankingSummary?: Record<string, unknown>;
};

export function TraceJsonPanel({ traceJson, rankingSummary }: TraceJsonPanelProps) {
  const [open, setOpen] = useState(false);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <CardTitle>Raw trace JSON</CardTitle>
        <Button type="button" variant="ghost" onClick={() => setOpen((current) => !current)}>
          {open ? "Hide JSON" : "Show JSON"}
        </Button>
      </CardHeader>
      {open ? (
        <CardContent className="space-y-4">
          <pre className="max-h-[520px] overflow-auto rounded-md border border-slate-800 bg-slate-950 p-4 text-xs text-slate-300">
            {JSON.stringify(traceJson, null, 2)}
          </pre>
          {rankingSummary ? (
            <pre className="max-h-80 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-4 text-xs text-slate-300">
              {JSON.stringify({ ranking_summary: rankingSummary }, null, 2)}
            </pre>
          ) : null}
        </CardContent>
      ) : null}
    </Card>
  );
}
