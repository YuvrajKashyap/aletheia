# Final Handoff

This handoff is for future Yuvraj or another assistant continuing from the completed Aletheia project state.

## Project Purpose

Aletheia is a production-style retrieval, reranking, evaluation, and search observability platform. It compares BM25, dense vector retrieval, hybrid Reciprocal Rank Fusion, and cross-encoder reranking over BEIR SciFact with real query traces, document-level evaluation, experiment comparison, replay workflows, index observability, and system health.

It is not a chatbot, not a generic RAG wrapper, and not a fake dashboard.

## Architecture Summary

- Frontend: Next.js, TypeScript, Tailwind CSS, Recharts.
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic.
- Metadata: PostgreSQL.
- Async jobs: Redis/RQ.
- Lexical retrieval: OpenSearch BM25.
- Dense retrieval: Qdrant vectors.
- Models: `BAAI/bge-small-en-v1.5` embeddings and `cross-encoder/ms-marco-MiniLM-L-6-v2` reranker.
- Public demo: Vercel snapshot mode using real exported local outputs.

## Local Run Commands

Start infra:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1
```

Start API:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1
```

Start worker:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/worker.ps1
```

Start web:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/web.ps1
```

## Public Demo Mode

The public demo is snapshot-backed. It reads real exported JSON under `apps/web/public/demo-data`. The public site does not run live arbitrary retrieval, reranking, index rebuilds, evaluation jobs, replay jobs, or admin actions. The full live stack runs locally.

## Key Docs To Read

- `README.md`
- `docs/docs-index.md`
- `docs/project-closeout.md`
- `docs/architecture.md`
- `docs/retrieval-design.md`
- `docs/evaluation.md`
- `docs/benchmark-results.md`
- `docs/public-demo-mode.md`
- `docs/final-resume-copy.md`
- `docs/interview-package.md`

## Final Verification Commands

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1
powershell -ExecutionPolicy Bypass -File scripts/powershell/ci-check.ps1
powershell -ExecutionPolicy Bypass -File scripts/powershell/repo-audit.ps1
```

## Final Resume, Portfolio, And Interview Copy

- Resume copy: `docs/final-resume-copy.md`
- Portfolio card: `docs/final-portfolio-card.md`
- LinkedIn/GitHub copy: `docs/final-linkedin-github-copy.md`
- Review notes: `docs/review-notes.md`
- Interview package: `docs/interview-package.md`
- Interview Q&A: `docs/interview-q-and-a.md`
- System design walkthrough: `docs/system-design-walkthrough.md`
- Engineering stories: `docs/engineering-stories.md`
- Scale plan: `docs/scale-plan.md`

## Refresh Snapshot Data

Run this from the repo root after generating real local outputs:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/export-demo-snapshot.ps1
```

Do not hand-edit snapshot JSON to improve presentation. Regenerate it from real local data.

## Run Final Benchmark Suite

Skip rerank for the faster full modes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-final-benchmark-suite.ps1 -SkipRerank
```

Run rerank separately:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-final-benchmark-suite.ps1 -OnlyMode hybrid_rerank
```

Generated benchmark JSON reports are ignored by default unless intentionally selected later.

## Run Golden Smoke

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-golden-smoke.ps1 -Mode hybrid -QueryLimit 5 -TopK 10
```

Golden smoke is a local full-stack check, not default GitHub CI.

## Update README Screenshots Later

- Capture real public snapshot or local live screenshots only.
- Place images under `docs/assets/screenshots`.
- Update `README.md` and `docs/screenshots.md`.
- Do not use fake images, generated mock screenshots, or edited screenshots that alter data.
