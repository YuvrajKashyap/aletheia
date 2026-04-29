# Atlas Integration Flow

This diagram shows a future integration where Atlas produces a web corpus and Aletheia provides retrieval, ranking, evaluation, and observability.

```mermaid
flowchart TD
  Frontier[Atlas URL frontier] --> Robots[Robots and politeness]
  Robots --> Crawler[Atlas crawler]
  Crawler --> Extractor[Extractor]
  Extractor --> Cleaned[Cleaned documents]
  Cleaned --> AtlasStore[Atlas Postgres store]

  AtlasStore --> Dataset[Aletheia dataset atlas_web_v1]
  Dataset --> Chunks[Chunking]
  Chunks --> OS[OpenSearch index]
  Chunks --> QD[Qdrant collection]

  OS --> Search[Aletheia search]
  QD --> Search
  Search --> Traces[Query traces]
  Search --> Replay[Replay]
  Labels[Optional human labeled qrels] --> Evaluation[Evaluation]
  Search --> Evaluation
```

## Notes

- This integration is future-facing and not implemented yet.
- Atlas produces the corpus.
- Aletheia provides retrieval, ranking, evaluation, replay, and search observability.
