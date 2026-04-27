"use client";

import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ExperimentMatrixRow } from "@/components/experiments/experiment-data";

type ExperimentQualityChartProps = {
  rows: ExperimentMatrixRow[];
};

export function ExperimentQualityChart({ rows }: ExperimentQualityChartProps) {
  const data = rows
    .filter(
      (row) =>
        typeof row.latestRun?.recall_at_10 === "number" ||
        typeof row.latestRun?.mrr_at_10 === "number" ||
        typeof row.latestRun?.ndcg_at_10 === "number"
    )
    .map((row) => ({
      name: row.config.name,
      recall_at_10: row.latestRun?.recall_at_10 ?? undefined,
      mrr_at_10: row.latestRun?.mrr_at_10 ?? undefined,
      ndcg_at_10: row.latestRun?.ndcg_at_10 ?? undefined
    }));
  const chartWidth = Math.max(760, data.length * 170);

  return (
    <Card className="min-w-0 overflow-hidden">
      <CardHeader>
        <CardTitle>Quality comparison</CardTitle>
        <CardDescription>Latest completed runs with real Recall@10, MRR@10, and NDCG@10 values.</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-slate-500">No real quality metrics are available for charting.</p>
        ) : (
          <div className="rounded-md border border-slate-800 bg-slate-950/40 p-3">
            <p className="mb-2 text-xs text-slate-500">Scroll horizontally to compare more configs.</p>
            <div
              aria-label="Experiment quality chart scroll area"
              className="w-full min-w-0 overflow-x-auto pb-3 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/70"
              tabIndex={0}
            >
              <BarChart data={data} height={280} margin={{ top: 8, right: 24, bottom: 8, left: 0 }} width={chartWidth}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: "#020617",
                    border: "1px solid #1e293b",
                    color: "#e2e8f0"
                  }}
                />
                <Legend wrapperStyle={{ color: "#cbd5e1" }} />
                <Bar dataKey="recall_at_10" fill="#67e8f9" name="Recall@10" />
                <Bar dataKey="mrr_at_10" fill="#a7f3d0" name="MRR@10" />
                <Bar dataKey="ndcg_at_10" fill="#fcd34d" name="NDCG@10" />
              </BarChart>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
