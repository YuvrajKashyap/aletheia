import { IndexStatusBadge } from "@/components/indexes/index-status-badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { OpenSearchHealthResponse, QdrantHealthResponse } from "@/lib/api/types";

type IndexHealthCardsProps = {
  openSearch: OpenSearchHealthResponse | null;
  qdrant: QdrantHealthResponse | null;
};

export function IndexHealthCards({ openSearch, qdrant }: IndexHealthCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <HealthCard
        title="OpenSearch"
        description="Lexical retrieval backend."
        status={openSearch?.status}
        fields={[
          ["URL", openSearch?.url],
          ["Cluster", openSearch?.cluster_name],
          ["Version", openSearch?.version],
          ["Error", openSearch?.error]
        ]}
      />
      <HealthCard
        title="Qdrant"
        description="Dense vector retrieval backend."
        status={qdrant?.status}
        fields={[
          ["URL", qdrant?.url],
          ["Version", qdrant?.version],
          ["Collections", qdrant?.collections_count],
          ["Error", qdrant?.error]
        ]}
      />
    </div>
  );
}

function HealthCard({
  title,
  description,
  status,
  fields
}: {
  title: string;
  description: string;
  status?: string;
  fields: Array<[string, string | number | null | undefined]>;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle>{title}</CardTitle>
          <IndexStatusBadge status={status} />
        </div>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {fields.map(([label, value]) => (
          <div className="grid gap-2 text-sm md:grid-cols-[120px_1fr]" key={label}>
            <div className="text-slate-500">{label}</div>
            <div className="break-all font-mono text-slate-200">
              {value === null || value === undefined || value === "" ? "Unavailable" : String(value)}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
