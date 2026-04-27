import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ReplayJsonPanel({
  title = "Raw JSON",
  value
}: {
  title?: string;
  value?: unknown;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {value === undefined || value === null ? (
          <p className="text-sm text-slate-400">Unavailable</p>
        ) : (
          <pre className="max-h-96 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs leading-5 text-slate-300">
            {typeof value === "string" ? value : JSON.stringify(value, null, 2)}
          </pre>
        )}
      </CardContent>
    </Card>
  );
}
