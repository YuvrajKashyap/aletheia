"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ReplayModeControls,
  buildReplayRequest,
  defaultReplayModeState,
  validateReplayModeState,
  type ReplayModeState
} from "@/components/replay/replay-mode-controls";
import {
  createSavedQuery,
  runGoldenReplay,
  runSavedQueryReplay,
  seedGoldenQueries
} from "@/lib/api/replay";
import type { ReplayResponse, SavedQueryItem } from "@/lib/api/types";
import { isSnapshotMode } from "@/lib/demo-mode";

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Request failed";
}

type Feedback = {
  scope: "admin" | "seed" | "create" | "single" | "golden";
  tone: "success" | "error";
  text: string;
};

export function ReplayAdminPanel({
  selectedQuery,
  onActionComplete,
  onJobStarted
}: {
  selectedQuery: SavedQueryItem | null;
  onActionComplete: () => void;
  onJobStarted: (response: ReplayResponse) => void;
}) {
  const snapshotMode = isSnapshotMode();
  const [adminApiKey, setAdminApiKey] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [seedLimit, setSeedLimit] = useState(10);
  const [manualName, setManualName] = useState("");
  const [manualText, setManualText] = useState("");
  const [manualSource, setManualSource] = useState("manual");
  const [modeState, setModeState] = useState<ReplayModeState>(defaultReplayModeState);
  const [sourceTraceId, setSourceTraceId] = useState("");
  const [indexVersionId, setIndexVersionId] = useState("");
  const [goldenName, setGoldenName] = useState("Replay Lab golden replay");
  const [goldenLimit, setGoldenLimit] = useState(3);
  const [goldenNotes, setGoldenNotes] = useState("");

  if (snapshotMode) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Admin actions disabled</CardTitle>
          <CardDescription>
            Replay actions are disabled in public snapshot mode. The rows above are real replay outputs exported from
            the full local stack.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  function setSuccess(scope: Feedback["scope"], text: string) {
    setFeedback({ scope, tone: "success", text });
  }

  function setError(scope: Feedback["scope"], text: string) {
    setFeedback({ scope, tone: "error", text });
  }

  function requireAdminKey() {
    if (!adminApiKey.trim()) {
      setError("admin", "Admin API key is required for replay actions.");
      return null;
    }
    return adminApiKey.trim();
  }

  async function runAction(scope: Feedback["scope"], action: (key: string) => Promise<void>) {
    const key = requireAdminKey();
    if (!key) return;
    setIsBusy(true);
    setFeedback(null);
    try {
      await action(key);
    } catch (err) {
      setError(scope, errorMessage(err));
    } finally {
      setIsBusy(false);
    }
  }

  function currentReplayRequest(scope: Feedback["scope"]) {
    const validation = validateReplayModeState(modeState);
    if (validation) {
      setError(scope, validation);
      return null;
    }
    return buildReplayRequest(modeState, { sourceTraceId, indexVersionId });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Local admin actions</CardTitle>
        <CardDescription>Seed, create, and replay saved queries through protected FastAPI endpoints.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <label className="block">
          <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Admin API key</span>
          <input
            className="mt-2 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
            type="password"
            value={adminApiKey}
            onChange={(event) => setAdminApiKey(event.target.value)}
          />
        </label>
        {feedback?.scope === "admin" ? <FeedbackAlert feedback={feedback} /> : null}

        <section className="space-y-3 rounded-lg border border-slate-800 bg-slate-950/40 p-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Seed golden queries</h3>
            <p className="mt-1 text-xs text-slate-500">Create missing SciFact golden saved queries from backend qrels.</p>
          </div>
          {feedback?.scope === "seed" ? <FeedbackAlert feedback={feedback} /> : null}
          <NumberField label="limit" value={seedLimit} onChange={setSeedLimit} />
          <Button
            disabled={isBusy}
            onClick={() =>
              runAction("seed", async (key) => {
                const result = await seedGoldenQueries(
                  { dataset_name: "beir/scifact", dataset_version: "test", limit: seedLimit, offset: 0 },
                  key
                );
                setSuccess("seed", `Seed complete. Created ${result.created_count ?? 0}, existing ${result.existing_count ?? 0}.`);
                onActionComplete();
              })
            }
          >
            Seed golden queries
          </Button>
        </section>

        <section className="space-y-3 rounded-lg border border-slate-800 bg-slate-950/40 p-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Create manual saved query</h3>
            <p className="mt-1 text-xs text-slate-500">Store a replayable query without generating answers.</p>
          </div>
          {feedback?.scope === "create" ? <FeedbackAlert feedback={feedback} /> : null}
          <TextField label="name optional" value={manualName} onChange={setManualName} />
          <TextField label="source" value={manualSource} onChange={setManualSource} />
          <label className="block">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">query text</span>
            <textarea
              className="mt-2 min-h-24 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              value={manualText}
              onChange={(event) => setManualText(event.target.value)}
            />
          </label>
          <Button
            disabled={isBusy}
            onClick={() =>
              runAction("create", async (key) => {
                if (!manualText.trim()) {
                  setError("create", "Saved query text is required.");
                  return;
                }
                await createSavedQuery(
                  { name: manualName.trim() || null, text: manualText.trim(), source: manualSource.trim() || "manual" },
                  key
                );
                setSuccess("create", "Manual saved query created.");
                setManualText("");
                onActionComplete();
              })
            }
          >
            Create saved query
          </Button>
        </section>

        <section className="space-y-3 rounded-lg border border-slate-800 bg-slate-950/40 p-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Replay selected saved query</h3>
            <p className="mt-1 text-xs text-slate-500">Queue one saved query replay through the selected retrieval settings.</p>
          </div>
          {feedback?.scope === "single" ? <FeedbackAlert feedback={feedback} /> : null}
          <p className="text-xs text-slate-500">
            Selected query: {selectedQuery?.name || selectedQuery?.id || "None selected"}
          </p>
          <ReplayModeControls state={modeState} onChange={setModeState} />
          <div className="grid gap-3 md:grid-cols-2">
            <TextField label="source_trace_id optional" value={sourceTraceId} onChange={setSourceTraceId} />
            <TextField label="index_version_id optional" value={indexVersionId} onChange={setIndexVersionId} />
          </div>
          <Button
            disabled={isBusy || !selectedQuery}
            onClick={() =>
              runAction("single", async (key) => {
                if (!selectedQuery) {
                  setError("single", "Select a saved query first.");
                  return;
                }
                const request = currentReplayRequest("single");
                if (!request) return;
                const response = await runSavedQueryReplay(selectedQuery.id, request, key);
                onJobStarted(response);
                setSuccess("single", response.message || "Saved query replay submitted.");
              })
            }
          >
            Replay selected query
          </Button>
        </section>

        <section className="space-y-3 rounded-lg border border-slate-800 bg-slate-950/40 p-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Run golden replay batch</h3>
            <p className="mt-1 text-xs text-slate-500">Queue a small golden replay batch for trace-level regression checks.</p>
          </div>
          {feedback?.scope === "golden" ? <FeedbackAlert feedback={feedback} /> : null}
          <TextField label="name" value={goldenName} onChange={setGoldenName} />
          <NumberField label="limit" value={goldenLimit} onChange={setGoldenLimit} />
          <TextField label="notes optional" value={goldenNotes} onChange={setGoldenNotes} />
          <Button
            disabled={isBusy}
            onClick={() =>
              runAction("golden", async (key) => {
                const request = currentReplayRequest("golden");
                if (!request) return;
                const response = await runGoldenReplay(
                  {
                    ...request,
                    name: goldenName.trim() || "Replay Lab golden replay",
                    source: "golden_scifact",
                    limit: goldenLimit,
                    offset: 0,
                    notes: goldenNotes.trim() || null
                  },
                  key
                );
                onJobStarted(response);
                setSuccess("golden", response.message || "Golden replay submitted.");
              })
            }
          >
            Run golden replay
          </Button>
        </section>

      </CardContent>
    </Card>
  );
}

function FeedbackAlert({ feedback }: { feedback: Feedback }) {
  const className =
    feedback.tone === "success"
      ? "rounded-md border border-emerald-900 bg-emerald-950/30 p-3 text-sm text-emerald-300"
      : "rounded-md border border-red-900 bg-red-950/30 p-3 text-sm text-red-300";

  return <p className={className}>{feedback.text}</p>;
}

function TextField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <input
        className="mt-2 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <input
        className="mt-2 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
        min={1}
        type="number"
        value={value}
        onChange={(event) => onChange(Number.parseInt(event.target.value, 10) || 1)}
      />
    </label>
  );
}
