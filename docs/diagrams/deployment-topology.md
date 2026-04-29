# Deployment Topology

This diagram shows current public hosting, local full-stack operation, and future optional hosted components.

```mermaid
flowchart TD
  GitHub[GitHub repo] --> Vercel[Vercel frontend]
  Vercel --> Snapshot[Static snapshot data]
  GitHub --> Neon[Neon migrated schema]

  Local[Local Docker Compose stack] --> LocalAPI[FastAPI]
  Local --> LocalPG[Postgres]
  Local --> LocalRedis[Redis RQ]
  Local --> LocalOS[OpenSearch]
  Local --> LocalQD[Qdrant]
  Local --> LocalWorker[Worker]
  Local --> LocalModels[Local models]

  FutureAPI[Future optional hosted FastAPI] -. future optional .-> FutureRedis[Future optional Redis]
  FutureAPI -. future optional .-> FutureOS[Future optional OpenSearch]
  FutureAPI -. future optional .-> FutureQD[Future optional Qdrant]
  FutureRedis -. future optional .-> FutureWorker[Future optional worker]
```

## Notes

- Current public demo is snapshot-hosted.
- Future live backend hosting is optional and cost-dependent.
- Future optional components are not currently deployed.
- Secrets must stay out of the repository.
