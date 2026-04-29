# Ingestion And Indexing Flow

This diagram shows how SciFact data becomes versioned lexical and vector indexes.

```mermaid
flowchart TD
  SciFact[ir datasets SciFact] --> Load[Load documents queries qrels]
  Load --> PG[PostgreSQL]
  PG --> Normalize[Normalize text]
  Normalize --> Chunks[Create document-level chunks]
  Chunks --> IndexVersion[Create index version]

  IndexVersion --> LexBuild[Build lexical index]
  LexBuild --> OpenSearch[OpenSearch]

  IndexVersion --> Embed[Generate embeddings]
  Embed --> VectorBuild[Build vector collection]
  VectorBuild --> Qdrant[Qdrant]

  LexBuild --> IndexJobs[Index jobs]
  VectorBuild --> IndexJobs
  IndexJobs --> Metadata[Index version metadata]
  Metadata --> Activate[Activate ready index version]
```

## Notes

- SciFact uses document-level chunks because qrels are document-level.
- Limited index builds must not corrupt corpus-level metadata.
- Failed jobs and failed index versions are tracked.
