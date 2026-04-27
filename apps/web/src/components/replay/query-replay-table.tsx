import Link from "next/link";

import { Button } from "@/components/ui/button";
import { ReplayStatusBadge } from "@/components/replay/replay-status-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { QueryReplayItem } from "@/lib/api/types";

function shortId(value?: string | null) {
  return value ? value.slice(0, 8) : "Unavailable";
}

function TraceLink({ traceId, label }: { traceId?: string | null; label: string }) {
  if (!traceId) {
    return <span className="text-slate-500">Unavailable</span>;
  }

  return (
    <div className="flex min-w-32 flex-col gap-1">
      <span className="font-mono text-xs text-slate-300">{shortId(traceId)}</span>
      <Link
        aria-label={`Open ${label} ${traceId}`}
        className="w-fit rounded-md border border-cyan-800 bg-cyan-950/30 px-2 py-0.5 text-xs font-medium text-cyan-200 underline-offset-4 hover:border-cyan-500 hover:text-cyan-100 hover:underline focus:outline-none focus:ring-2 focus:ring-cyan-400/70"
        href={`/traces?traceId=${encodeURIComponent(traceId)}`}
        title={`Open trace ${traceId}`}
      >
        Open trace
      </Link>
    </div>
  );
}

export function QueryReplayTable({
  replays,
  selectedReplayId,
  onSelect
}: {
  replays: QueryReplayItem[];
  selectedReplayId?: string | null;
  onSelect: (replay: QueryReplayItem) => void;
}) {
  if (!replays.length) {
    return <p className="rounded-lg border border-slate-800 p-4 text-sm text-slate-400">No query replays found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Status</TableHead>
            <TableHead>Saved query</TableHead>
            <TableHead>Target trace</TableHead>
            <TableHead>Source trace</TableHead>
            <TableHead>Experiment config</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Completed</TableHead>
            <TableHead>Error</TableHead>
            <TableHead className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
              Action
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {replays.map((replay) => {
            const isSelected = selectedReplayId === replay.id;
            return (
              <TableRow key={replay.id} className={isSelected ? "bg-cyan-950/20" : undefined}>
              <TableCell>
                <ReplayStatusBadge status={replay.status} />
              </TableCell>
              <TableCell className="font-mono text-xs">{shortId(replay.saved_query_id)}</TableCell>
              <TableCell>
                <TraceLink traceId={replay.target_trace_id} label="target trace" />
              </TableCell>
              <TableCell>
                <TraceLink traceId={replay.source_trace_id} label="source trace" />
              </TableCell>
              <TableCell className="font-mono text-xs">{shortId(replay.experiment_config_id)}</TableCell>
              <TableCell className="whitespace-nowrap text-xs">{replay.created_at || "Unavailable"}</TableCell>
              <TableCell className="whitespace-nowrap text-xs">{replay.completed_at || "Unavailable"}</TableCell>
              <TableCell className="max-w-64 truncate text-red-300">{replay.error_message || ""}</TableCell>
              <TableCell className="sticky right-0 bg-slate-950 text-right shadow-[-12px_0_18px_rgba(2,6,23,0.85)]">
                <Button variant="secondary" onClick={() => onSelect(replay)}>
                  {isSelected ? "Selected" : "View detail"}
                </Button>
              </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
