"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getEvaluationRunChartLabel } from "@/components/evaluations/evaluation-run-labels";
import type { EvaluationRunItem } from "@/lib/api/types";

type LatencyChartProps = {
  runs: EvaluationRunItem[];
};

export function EvaluationLatencyChart({ runs }: LatencyChartProps) {
  const data = runs
    .filter((run) => run.avg_latency_ms !== null || run.p50_latency_ms !== null || run.p95_latency_ms !== null)
    .slice(0, 10)
    .map((run) => ({
      name: getEvaluationRunChartLabel(run),
      avg_latency_ms: run.avg_latency_ms ?? undefined,
      p50_latency_ms: run.p50_latency_ms ?? undefined,
      p95_latency_ms: run.p95_latency_ms ?? undefined
    }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Latency comparison</CardTitle>
        <CardDescription>Recent runs with real measured latency fields.</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-slate-500">No latency values available for charting.</p>
        ) : (
          <div className="h-72">
            <ResponsiveContainer height="100%" width="100%">
              <BarChart data={data}>
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
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
