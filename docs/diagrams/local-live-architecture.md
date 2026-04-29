# Local Live Architecture

This diagram shows the full local Aletheia stack used for live retrieval, indexing, evaluation, replay, tracing, and snapshot export.

```mermaid
flowchart TD
  User[User browser] --> Web[Next.js frontend]
  Web --> API[FastAPI API]

  API --> PG[PostgreSQL]
  API --> Redis[Redis queue]
  Redis --> Worker[RQ worker]

  API --> OS[OpenSearch BM25]
  API --> QD[Qdrant vectors]
  API --> Emb[Local embedding model]
  API --> Rank[Local reranker model]

  Worker --> PG
  Worker --> OS
  Worker --> QD
  Worker --> Emb
  Worker --> Rank

  PG --> Traces[Query traces]
  PG --> Eval[Evaluation runs]
  PG --> Jobs[Index jobs]
  PG --> Events[System events]
  PG --> Heartbeats[Worker heartbeats]
```

## Notes

- This is the full live local stack.
- Services run through Docker Compose and local processes.
- This stack generates the real outputs used by public snapshot exports.
- This full stack is not currently hosted publicly.
