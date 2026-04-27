import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function MetadataJsonPanel({
  title = "Metadata JSON",
  value
}: {
  title?: string;
  value?: Record<string, unknown> | null;
}) {
  const hasValue = value && Object.keys(value).length > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {hasValue ? (
          <pre className="max-h-72 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs leading-5 text-slate-300">
            {JSON.stringify(value, null, 2)}
          </pre>
        ) : (
          <p className="text-sm text-slate-400">No metadata available.</p>
        )}
      </CardContent>
    </Card>
  );
}
