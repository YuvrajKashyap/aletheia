import Link from "next/link";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SystemEventSeverityBadge } from "@/components/system/system-event-severity-badge";
import type { SystemEventItem } from "@/lib/api/types";

function short(value?: string | null) {
  return value ? value.slice(0, 12) : "Unavailable";
}

export function SystemEventsTable({
  events,
  total,
  error,
  severity,
  eventType,
  limit,
  onSeverityChange,
  onEventTypeChange,
  onLimitChange
}: {
  events: SystemEventItem[];
  total?: number;
  error?: string | null;
  severity: string;
  eventType: string;
  limit: number;
  onSeverityChange: (value: string) => void;
  onEventTypeChange: (value: string) => void;
  onLimitChange: (value: number) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>System events</CardTitle>
        <CardDescription>Recent backend system events from the `system_events` table.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 md:grid-cols-[160px_1fr_120px]">
          <label className="grid gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Severity</span>
            <select
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              value={severity}
              onChange={(event) => onSeverityChange(event.target.value)}
            >
              <option value="all">all</option>
              <option value="info">info</option>
              <option value="warning">warning</option>
              <option value="error">error</option>
            </select>
          </label>
          <label className="grid gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Event type</span>
            <input
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              placeholder="optional exact event type"
              value={eventType}
              onChange={(event) => onEventTypeChange(event.target.value)}
            />
          </label>
          <label className="grid gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Limit</span>
            <select
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              value={limit}
              onChange={(event) => onLimitChange(Number(event.target.value))}
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </label>
        </div>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        {!error && !events.length ? <p className="text-sm text-slate-400">No system events matched the current filters.</p> : null}
        {events.length ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Severity</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Message</TableHead>
                  <TableHead>Request</TableHead>
                  <TableHead>Job</TableHead>
                  <TableHead>Trace</TableHead>
                  <TableHead>Created</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {events.map((event) => (
                  <TableRow key={event.id}>
                    <TableCell>
                      <SystemEventSeverityBadge severity={event.severity} />
                    </TableCell>
                    <TableCell className="font-mono text-xs">{event.event_type}</TableCell>
                    <TableCell className="min-w-72 text-slate-200">{event.message}</TableCell>
                    <TableCell className="font-mono text-xs">{short(event.request_id)}</TableCell>
                    <TableCell className="font-mono text-xs">{short(event.job_id)}</TableCell>
                    <TableCell className="font-mono text-xs">
                      {event.trace_id ? (
                        <Link className="text-cyan-200 underline-offset-4 hover:underline" href={`/traces?traceId=${encodeURIComponent(event.trace_id)}`}>
                          {short(event.trace_id)}
                        </Link>
                      ) : (
                        "Unavailable"
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-xs">{event.created_at || "Unavailable"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : null}
        {!error ? <p className="text-xs text-slate-500">{total ?? 0} events available for the current filters.</p> : null}
      </CardContent>
    </Card>
  );
}
