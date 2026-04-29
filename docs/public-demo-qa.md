# Public Demo QA Checklist

Public URL:

```text
https://aletheia.yuvrajkashyap.com
```

Fallback URL:

```text
https://aletheia-jade.vercel.app
```

Required Vercel environment:

```text
NEXT_PUBLIC_DEMO_MODE=snapshot
```

## Expected Public Behavior

- Snapshot banner is visible.
- App shell says snapshot data layer, not live API layer.
- Pages read from `/demo-data` exports.
- No live backend is required for browsing.
- No fake data, fake traces, fake metrics, or fake health is displayed.
- Admin and live actions are disabled in public snapshot mode.
- Trace links open `/traces?traceId=<trace_id>`.
- Evaluation links open `/evaluations?runId=<evaluation_run_id>` when available.

## Route Checklist

- `/`
  - Overview loads snapshot summary cards.
  - Counts and latest records come from exported data.
- `/search`
  - Curated public demo scenarios are visible.
  - Selecting a scenario loads real precomputed results.
  - Metadata shows trace ID and available index metadata.
  - Arbitrary live retrieval is not presented as hosted.
- `/traces`
  - Trace list loads from snapshot data.
  - Trace detail loads through direct selection and deep links.
  - Candidate provenance and raw trace JSON render when exported.
- `/evaluations`
  - Evaluation runs, charts, reports, and query results load from snapshot data.
  - `/evaluations?runId=<id>` selects the exported run.
- `/experiments`
  - Experiment configs and best-by-metric indicators use exported real metrics.
  - Admin comparison jobs are disabled.
- `/indexes`
  - Index status, versions, and jobs load from exported metadata.
  - Live rebuild and lifecycle actions are disabled.
- `/datasets`
  - Dataset stats and representative samples load from exported files.
  - Document, chunk, query, and qrel detail panels work for sampled records.
- `/replay`
  - Saved queries and replay runs load from exported replay data.
  - Replay metrics and matched or missed document IDs render when present.
  - Replay admin actions are disabled.
- `/system`
  - Snapshot system state loads from `/demo-data/system.json`.
  - Hosted/static state is clearly separated from local-only infrastructure.
  - System events render from exported data.

## Local-Only Systems

These systems run in the full local stack and are not hosted in public snapshot mode:

- FastAPI
- Redis/RQ
- OpenSearch
- Qdrant
- embedding model
- reranker

## Source of Truth

Public snapshot data is generated from the full local Aletheia pipeline. Regenerate it with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/export-demo-snapshot.ps1
```

Do not hand-edit generated snapshot JSON for demo polish. Update the exporter or frontend adapters instead.
