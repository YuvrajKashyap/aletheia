import { formatCount, formatDate, shortId } from "@/components/indexes/index-format";
import { IndexProgressBar } from "@/components/indexes/index-progress-bar";
import { IndexStatusBadge } from "@/components/indexes/index-status-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { IndexJobItem } from "@/lib/api/types";

type IndexJobTableProps = {
  jobs: IndexJobItem[];
};

export function IndexJobTable({ jobs }: IndexJobTableProps) {
  if (jobs.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
        No index jobs returned by FastAPI.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <Table className="min-w-[1100px]">
        <TableHeader>
          <TableRow>
            <TableHead>Job</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Progress</TableHead>
            <TableHead>Total</TableHead>
            <TableHead>Completed</TableHead>
            <TableHead>Failed</TableHead>
            <TableHead>Error</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Completed at</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobs.map((job) => (
            <TableRow key={job.id}>
              <TableCell>
                <div className="font-mono text-xs text-slate-200">{shortId(job.job_id || job.id)}</div>
                <div className="mt-1 font-mono text-xs text-slate-500">{shortId(job.index_version_id)}</div>
              </TableCell>
              <TableCell>{job.job_type}</TableCell>
              <TableCell>
                <IndexStatusBadge status={job.status} />
              </TableCell>
              <TableCell>
                <IndexProgressBar completed={job.chunks_completed} total={job.chunks_total} />
              </TableCell>
              <TableCell className="font-mono">{formatCount(job.chunks_total)}</TableCell>
              <TableCell className="font-mono">{formatCount(job.chunks_completed)}</TableCell>
              <TableCell className="font-mono">{formatCount(job.chunks_failed)}</TableCell>
              <TableCell className="max-w-72 truncate text-red-300">{job.error_message || "None"}</TableCell>
              <TableCell>{formatDate(job.created_at)}</TableCell>
              <TableCell>{formatDate(job.completed_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
