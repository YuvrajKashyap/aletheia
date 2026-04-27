import { formatCount } from "@/components/indexes/index-format";
import { IndexStatusBadge } from "@/components/indexes/index-status-badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { IndexStatusResponse } from "@/lib/api/types";

type IndexStatusCardsProps = {
  status: IndexStatusResponse | null;
};

export function IndexStatusCards({ status }: IndexStatusCardsProps) {
  const active = status?.active_index_version || null;

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Card>
        <CardHeader>
          <CardTitle>Active version</CardTitle>
          <CardDescription>Confirmed by FastAPI index status.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="text-sm font-medium text-slate-100">{active?.name || "Unavailable"}</div>
          <IndexStatusBadge status={active?.status} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Corpus counts</CardTitle>
          <CardDescription>Stored index metadata.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-3 gap-3 text-sm">
          <Metric label="Docs" value={formatCount(active?.document_count)} />
          <Metric label="Chunks" value={formatCount(active?.chunk_count)} />
          <Metric label="Vectors" value={formatCount(active?.vector_count)} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Lexical index</CardTitle>
          <CardDescription>OpenSearch index name.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="break-all font-mono text-sm text-slate-200">{active?.lexical_index_name || "Unavailable"}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Vector collection</CardTitle>
          <CardDescription>Qdrant collection name.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="break-all font-mono text-sm text-slate-200">{active?.vector_collection_name || "Unavailable"}</div>
        </CardContent>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 font-mono text-slate-100">{value}</div>
    </div>
  );
}
