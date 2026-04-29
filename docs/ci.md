# CI and Quality Gates

Aletheia CI is a fast correctness gate for code quality, type safety, and repository structure. It is intentionally scoped to deterministic checks that do not require local infrastructure.

## What CI Runs

- Backend unit tests with `pytest`
- Backend linting with `ruff`
- Frontend TypeScript typecheck
- Frontend lint
- Frontend Next.js build in snapshot mode
- Repository doctor

## What CI Does Not Run

- Docker Compose
- OpenSearch, Qdrant, Redis, or worker processes
- SciFact ingestion or chunking
- Index builds
- Evaluation runs
- Hugging Face model downloads

## Why

CI is a fast correctness gate. It should catch broken tests, lint failures, type errors, broken snapshot builds, and missing required files without starting expensive infrastructure.

Full retrieval integration remains local-only because it depends on Docker services, search indexes, vector collections, queue workers, and model availability. Those checks are validated manually or through dedicated local scripts.

## Local Reproduction

Run the same fast quality gate locally:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/ci-check.ps1
```

## Reading Failures

- Backend test failures usually point to API, service, schema, or serialization regressions.
- Ruff failures are formatting, import, or static quality issues in backend Python code.
- Frontend typecheck failures indicate TypeScript contract or component typing issues.
- Frontend lint failures indicate UI code quality issues.
- Snapshot build failures mean the public Vercel demo build path is broken.
- Doctor failures mean expected project files or folders are missing.

## Future Improvements

- Optional Docker smoke workflow
- Dedicated integration test workflow
- Lightweight evaluation smoke test
