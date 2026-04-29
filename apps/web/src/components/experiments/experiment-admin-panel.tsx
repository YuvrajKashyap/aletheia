"use client";

import { useState } from "react";

import { ExperimentJobStatus } from "@/components/experiments/experiment-job-status";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/client";
import { getJobStatus, seedDefaultExperimentConfigs, startComparisonJob } from "@/lib/api/experiments";
import type { JobStatusResponse, StartComparisonResponse } from "@/lib/api/types";
import { isSnapshotMode } from "@/lib/demo-mode";

type ExperimentAdminPanelProps = {
  onDataChanged: () => void;
};

export function ExperimentAdminPanel({ onDataChanged }: ExperimentAdminPanelProps) {
  const snapshotMode = isSnapshotMode();
  const [isOpen, setIsOpen] = useState(false);
  const [adminApiKey, setAdminApiKey] = useState("");
  const [comparisonName, setComparisonName] = useState("Default experiment comparison");
  const [queryLimit, setQueryLimit] = useState(3);
  const [notes, setNotes] = useState("Triggered from local Experiment Matrix UI");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isJobLoading, setIsJobLoading] = useState(false);
  const [startedJob, setStartedJob] = useState<StartComparisonResponse | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [jobError, setJobError] = useState<string | null>(null);

  if (snapshotMode) {
    return (
      <Card className="border-cyan-900/60 bg-cyan-950/10">
        <CardHeader>
          <CardTitle>Public snapshot actions</CardTitle>
          <CardDescription>
            Admin comparison jobs are intentionally disabled in public snapshot mode.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-6 text-slate-400">
            The experiment rows and metrics are real exported outputs. Run the full local stack to seed configs or launch
            new comparison jobs.
          </p>
        </CardContent>
      </Card>
    );
  }

  async function seedDefaults() {
    setIsSubmitting(true);
    setError(null);
    setMessage(null);
    try {
      const response = await seedDefaultExperimentConfigs(adminApiKey);
      setMessage(
        `Seed complete. Created ${response.created_count ?? 0}, updated ${
          response.updated_count ?? 0
        }, existing ${response.existing_count ?? 0}.`
      );
      onDataChanged();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function startComparison() {
    setIsSubmitting(true);
    setError(null);
    setMessage(null);
    setStartedJob(null);
    setJobStatus(null);
    setJobError(null);
    try {
      const response = await startComparisonJob(
        {
          name: comparisonName.trim() || "Default experiment comparison",
          use_defaults: true,
          query_limit: queryLimit,
          query_offset: 0,
          notes: notes.trim() || null
        },
        adminApiKey
      );
      setStartedJob(response);
      setMessage(response.message || `Comparison job queued: ${response.job_id}`);
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function refreshJob() {
    if (!startedJob?.job_id) {
      return;
    }
    setIsJobLoading(true);
    setJobError(null);
    try {
      const response = await getJobStatus(startedJob.job_id);
      setJobStatus(response);
      if (response.status === "finished") {
        onDataChanged();
      }
    } catch (caught) {
      setJobError(errorMessage(caught));
    } finally {
      setIsJobLoading(false);
    }
  }

  return (
    <Card className="border-slate-800 bg-slate-950/70">
      <CardHeader>
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <CardTitle>Admin actions</CardTitle>
            <CardDescription>
              Local actions call admin-protected FastAPI endpoints. The API key stays in component state only.
            </CardDescription>
          </div>
          <Button type="button" onClick={() => setIsOpen((current) => !current)}>
            {isOpen ? "Hide actions" : "Show actions"}
          </Button>
        </div>
      </CardHeader>
      {isOpen ? (
        <CardContent className="space-y-4">
          <label className="grid gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Admin API key</span>
            <input
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              type="password"
              value={adminApiKey}
              onChange={(event) => setAdminApiKey(event.target.value)}
            />
          </label>
          <div className="grid gap-3 md:grid-cols-[1fr_140px]">
            <label className="grid gap-2">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Comparison name</span>
              <input
                className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                value={comparisonName}
                onChange={(event) => setComparisonName(event.target.value)}
              />
            </label>
            <label className="grid gap-2">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Query limit</span>
              <input
                className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                min={1}
                max={300}
                type="number"
                value={queryLimit}
                onChange={(event) => setQueryLimit(Number(event.target.value))}
              />
            </label>
          </div>
          <label className="grid gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Notes</span>
            <textarea
              className="min-h-20 rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>
          <div className="flex flex-wrap gap-2">
            <Button disabled={isSubmitting || !adminApiKey.trim()} type="button" onClick={seedDefaults}>
              Seed default configs
            </Button>
            <Button
              disabled={isSubmitting || !adminApiKey.trim() || queryLimit < 1 || queryLimit > 300}
              type="button"
              variant="primary"
              onClick={startComparison}
            >
              Run default comparison
            </Button>
          </div>
          {message ? <p className="text-sm text-emerald-300">{message}</p> : null}
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
          <ExperimentJobStatus
            error={jobError}
            isLoading={isJobLoading}
            jobStatus={jobStatus}
            startedJob={startedJob}
            onRefresh={refreshJob}
          />
        </CardContent>
      ) : null}
    </Card>
  );
}

function errorMessage(caught: unknown): string {
  if (caught instanceof ApiError) {
    return caught.status === 401 ? "Admin API key was rejected by FastAPI." : caught.message;
  }
  if (caught instanceof Error) {
    return caught.message;
  }
  return "Request failed.";
}
