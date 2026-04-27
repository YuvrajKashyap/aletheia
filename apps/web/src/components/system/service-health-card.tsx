import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { OperationalStatusBadge, type OperationalStatus } from "@/components/system/operational-status-badge";

export type ServiceField = {
  label: string;
  value?: string | number | boolean | null;
  mono?: boolean;
  tone?: "normal" | "error";
};

export function ServiceHealthCard({
  title,
  description,
  status,
  fields,
  error
}: {
  title: string;
  description: string;
  status: OperationalStatus;
  fields: ServiceField[];
  error?: string | null;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle>{title}</CardTitle>
          <OperationalStatusBadge status={status} />
        </div>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {fields.map((field) => (
          <FieldRow field={field} key={field.label} />
        ))}
        {error ? <FieldRow field={{ label: "Error", value: error, tone: "error" }} /> : null}
      </CardContent>
    </Card>
  );
}

function FieldRow({ field }: { field: ServiceField }) {
  const missing = field.value === null || field.value === undefined || field.value === "";
  return (
    <div className="grid gap-2 text-sm md:grid-cols-[130px_1fr]">
      <div className="text-slate-500">{field.label}</div>
      <div
        className={[
          "break-all",
          field.mono ? "font-mono text-xs" : "",
          field.tone === "error" ? "text-red-300" : "text-slate-200"
        ].join(" ")}
      >
        {missing ? "Unavailable" : String(field.value)}
      </div>
    </div>
  );
}
