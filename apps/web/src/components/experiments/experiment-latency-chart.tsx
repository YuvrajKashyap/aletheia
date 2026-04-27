"use client";

import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ExperimentMatrixRow } from "@/components/experiments/experiment-data";

type ExperimentLatencyChartProps = {
  rows: ExperimentMatrixRow[];
};

export function ExperimentLatencyChart({ rows }: ExperimentLatencyChartProps) {
  const data = rows
    .filter(
      (row) =>
        typeof row.latestRun?.avg_latency_ms === "number" ||
        typeof row.latestRun?.p50_latency_ms === "number" ||
        typeof row.latestRun?.p95_latency_ms === "number"
    )
    .map((row) => ({
      name: row.config.name,
      avg_latency_ms: row.latestRun?.avg_latency_ms ?? undefined,
      p50_latency_ms: row.latestRun?.p50_latency_ms ?? undefined,
      p95_latency_ms: row.latestRun?.p95_latency_ms ?? undefined
    }));
  const chartWidth = Math.max(760, data.length * 170);

  return (
    <Card className="min-w-0 overflow-hidden">
      <CardHeader>
        <CardTitle>Latency comparison</CardTitle>
        <CardDescription>Latest completed runs with real measured latency fields.</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-slate-500">No real latency values are available for charting.</p>
        ) : (
          <div className="rounded-md border border-slate-800 bg-slate-950/40 p-3">
            <p className="mb-2 text-xs text-slate-500">Scroll horizontally to compare more configs.</p>
            <div
              aria-label="Experiment latency chart scroll area"
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
                <Bar dataKey="avg_latency_ms" fill="#67e8f9" name="Avg latency" />
                <Bar dataKey="p50_latency_ms" fill="#a7f3d0" name="p50" />
                <Bar dataKey="p95_latency_ms" fill="#fca5a5" name="p95" />
              </BarChart>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
