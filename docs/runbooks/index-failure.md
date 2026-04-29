# Runbook: Index Failure

## Symptoms

- Index build job fails.
- Index Console shows failed or incomplete index jobs.
- OpenSearch count does not match expected corpus count.
- Qdrant point count does not match expected vector count.
- Search returns missing or stale results.

## Check Services

Confirm local Docker services are running:

- Postgres
- OpenSearch
- Qdrant
- Redis

Use the Index Console and System Health page for current service state.

## Check Index Jobs

Inspect `index_jobs` through the Index Console:

- job type
- status
- chunks total
- chunks completed
- chunks failed
- error message
- linked job ID

## Check Search Backends

For OpenSearch:

- verify lexical index name
- verify document count
- inspect index build error messages

For Qdrant:

- verify collection name
- verify point count
- inspect vector build error messages

## Check Index Version Metadata

Index version fields should represent corpus-level metadata:

- `document_count`
- `chunk_count`
- `vector_count`

Limited build jobs should update job-level progress only. They should not reduce corpus-level counts.

## Rerun Builds

Use admin-protected local actions or PowerShell scripts:

- rerun lexical build
- rerun vector build
- start with a small limit for operational validation
- avoid destructive rebuilds unless intended

## Activation And Rollback

- Failed indexes should not activate automatically.
- Active index changes should be explicit.
- Rollback should select a known ready index version.
- Confirm one active index version after activation or rollback.
