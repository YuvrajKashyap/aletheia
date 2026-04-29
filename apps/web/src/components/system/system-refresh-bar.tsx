import { Button } from "@/components/ui/button";

export function SystemRefreshBar({
  isLoading,
  lastRefreshedAt,
  failedCount,
  snapshotMode = false,
  onRefresh
}: {
  isLoading: boolean;
  lastRefreshedAt: Date | null;
  failedCount: number;
  snapshotMode?: boolean;
  onRefresh: () => void;
}) {
  const loadedMessage = snapshotMode
    ? "Snapshot system state loaded from /demo-data/system.json."
    : "System checks loaded from FastAPI.";
  const loadingMessage = snapshotMode
    ? "Loading public snapshot system state."
    : "Loading system health from FastAPI.";

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-4">
      <div className="text-sm text-slate-400">
        {isLoading
          ? loadingMessage
          : failedCount
            ? `${failedCount} system checks failed.`
            : loadedMessage}
        <span className="ml-2 font-mono text-xs text-slate-500">
          Last refreshed {lastRefreshedAt ? lastRefreshedAt.toLocaleString() : "Unavailable"}
        </span>
      </div>
      <Button disabled={isLoading} type="button" onClick={onRefresh}>
        Refresh
      </Button>
    </div>
  );
}
