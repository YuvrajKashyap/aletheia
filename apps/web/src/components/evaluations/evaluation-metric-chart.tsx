"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { EvaluationRunItem } from "@/lib/api/types";

type ChartRun = {
  name: string;
  recall_at_10?: number;
  mrr_at_10?: number;
  ndcg_at_10?: number;
};

type MetricChartProps = {
  runs: EvaluationRunItem[];
};

function shortName(name: string): string {
  return name.length > 18 ? `${name.slice(0, 18)}...` : name;
}

export function EvaluationMetricChart({ runs }: MetricChartProps) {
  const data: ChartRun[] = runs
    .filter((run) => run.recall_at_10 !== null || run.mrr_at_10 !== null || run.ndcg_at_10 !== null)
    .slice(0, 10)
    .map((run) => ({
      name: shortName(run.name),
      recall_at_10: run.recall_at_10 ?? undefined,
      mrr_at_10: run.mrr_at_10 ?? undefined,
      ndcg_at_10: run.ndcg_at_10 ?? undefined
    }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Metric comparison</CardTitle>
        <CardDescription>Recent runs with real Recall@10, MRR@10, and NDCG@10 values.</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-slate-500">No numeric metric values available for charting.</p>
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
                <Bar dataKey="recall_at_10" fill="#67e8f9" name="Recall@10" />
                <Bar dataKey="mrr_at_10" fill="#a7f3d0" name="MRR@10" />
                <Bar dataKey="ndcg_at_10" fill="#fcd34d" name="NDCG@10" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
