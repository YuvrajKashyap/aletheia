# Aletheia Product Spec



## Product overview



Aletheia is a production-style hybrid retrieval, reranking, evaluation, and search observability platform.



The product exists to demonstrate a real retrieval system end to end. It ingests a benchmark corpus, stores documents and relevance judgments, builds lexical and dense indexes, executes multiple retrieval modes, reranks candidates, evaluates retrieval quality, stores query traces, and exposes the system through a polished technical dashboard.



Aletheia is not a chatbot, not a generic RAG wrapper, not a vector database demo, and not a fake dashboard. The system should prove competence in retrieval infrastructure, search evaluation, backend architecture, data modeling, observability, and product presentation.



The final system uses BEIR SciFact as the benchmark dataset. The final demo must be grounded in real SciFact documents, real SciFact queries, real SciFact qrels, real retrieval results, real evaluation metrics, and real latency measurements.



## Product goals



Aletheia should allow a user to:



\- Ingest the BEIR SciFact corpus.

\- Build a document and chunk store in PostgreSQL.

\- Build a BM25 index in OpenSearch.

\- Build a dense vector index in Qdrant.

\- Search with BM25, dense retrieval, hybrid RRF, and hybrid plus reranker.

\- Inspect how a query moved through the retrieval pipeline.

\- See candidate results, scores, rank changes, reranker effects, and latency.

\- Run evaluation jobs against real relevance judgments.

\- Compare retrieval experiments across modes and index versions.

\- Inspect index build state, active versions, failed versions, and job status.

\- Browse documents, chunks, metadata, and relevance information.

\- Monitor backend, database, OpenSearch, Qdrant, Redis, worker, and system events.



## Product non-goals



Aletheia should not become:



\- A chatbot.

\- A conversational search assistant.

\- A generic RAG app.

\- A frontend-only dashboard.

\- A notebook project.

\- A simple vector database demo.

\- An OpenAI API wrapper.

\- A fake metrics dashboard.

\- A hardcoded search demo.

\- A system where the frontend talks directly to the database.

\- A system where demo numbers are invented for visual polish.



## Intended users



The primary intended users are technical reviewers:



\- Software engineers

\- Backend engineers

\- ML infrastructure engineers

\- Search engineers

\- Recruiters with technical evaluation support

\- Technical founders or hiring managers reviewing portfolio depth



The product should communicate that the builder understands how retrieval systems work beyond surface-level AI application development.



## User-facing pages



### 1. Search Lab



Purpose:



Search Lab is the main query execution interface.



The user should be able to enter a query and select a retrieval mode:



\- BM25

\- Dense

\- Hybrid RRF

\- Hybrid plus reranker



Expected functionality:



\- Submit a query.

\- Select retrieval mode.

\- Select active or available index version where relevant.

\- Set top k where appropriate.

\- View ranked results.

\- View document IDs and chunk IDs.

\- View document titles or short text previews.

\- View retrieval scores.

\- View reranker scores when reranking is enabled.

\- View latency summary.

\- Open the query trace for the search.

\- Clearly distinguish document-level result identity from chunk-level retrieval evidence.



Final rule:



Search Lab must use real backend retrieval results. It must not use fake results in the final demo.



### 2. Query Trace



Purpose:



Query Trace explains what happened inside a single search request.



Expected functionality:



\- Show query text.

\- Show retrieval mode.

\- Show trace ID.

\- Show request ID where available.

\- Show active index version.

\- Show retrieval stages.

\- Show BM25 candidates when used.

\- Show dense candidates when used.

\- Show RRF fusion output when used.

\- Show reranker input candidates when used.

\- Show reranker output rankings when used.

\- Show rank changes before and after reranking.

\- Show chunk to document mapping.

\- Show document-level deduplication where relevant.

\- Show latency by stage.

\- Show total latency.

\- Show errors or partial failures if any stage failed.



Trace stages may include:



\- Request received

\- Query normalization

\- BM25 retrieval

\- Dense embedding

\- Dense retrieval

\- RRF fusion

\- Candidate deduplication

\- Reranking

\- Document hydration

\- Response generation

\- Trace persistence



Final rule:



Query Trace must represent real stored traces from backend execution.



### 3. Evaluation Dashboard



Purpose:



Evaluation Dashboard shows the quality and performance of retrieval modes using real SciFact qrels.



Expected functionality:



\- Show evaluation runs.

\- Show retrieval mode for each run.

\- Show index version for each run.

\- Show reranker setting for each run.

\- Show dataset name.

\- Show run status.

\- Show run timestamp.

\- Show number of evaluated queries.

\- Show Recall@5.

\- Show Recall@10.

\- Show MRR@10.

\- Show NDCG@10.

\- Show p50 latency.

\- Show p95 latency.

\- Show failures or partial runs honestly.

\- Allow filtering by mode, index version, and status where useful.



Final rule:



Metrics must be computed from real evaluation jobs. They must not be hardcoded.



### 4. Experiment Comparison



Purpose:



Experiment Comparison helps compare retrieval configurations.



Expected functionality:



\- Compare BM25 against dense retrieval.

\- Compare BM25 against hybrid RRF.

\- Compare hybrid RRF against hybrid plus reranker.

\- Compare different index versions.

\- Compare different evaluation runs.

\- Show metric deltas.

\- Show latency deltas.

\- Show quality versus latency tradeoffs.

\- Show run metadata.

\- Show whether each run completed successfully.



Useful comparisons:



\- Recall@10 improvement from BM25 to hybrid RRF.

\- MRR@10 improvement from hybrid RRF to hybrid plus reranker.

\- p95 latency increase from reranking.

\- Best quality mode.

\- Fastest mode.

\- Best quality to latency balance.



Final rule:



Experiment comparisons must use stored evaluation run data.



### 5. Index Console



Purpose:



Index Console shows ingestion, indexing, and active index state.



Expected functionality:



\- Show corpus ingestion status.

\- Show document count.

\- Show chunk count.

\- Show query count.

\- Show qrel count.

\- Show OpenSearch index versions.

\- Show Qdrant collection versions.

\- Show active lexical index version.

\- Show active vector index version.

\- Show failed index builds.

\- Show pending index jobs.

\- Show completed index jobs.

\- Show job IDs.

\- Show job timestamps.

\- Show job errors where available.

\- Allow protected admin actions later.



Protected admin actions may include:



\- Ingest dataset

\- Build BM25 index

\- Build dense index

\- Activate index version

\- Run evaluation

\- Retry failed job



Final rule:



Failed indexes must never auto-activate.



### 6. Document Explorer



Purpose:



Document Explorer allows inspection of stored corpus content.



Expected functionality:



\- Browse documents.

\- Search or filter documents.

\- View document ID.

\- View title where available.

\- View abstract or text.

\- View metadata.

\- View chunks for a document.

\- View chunk IDs.

\- View chunk text.

\- View chunk order.

\- View query relevance information where available.

\- View which queries mark the document relevant through qrels.

\- Support pagination and filtering.



Final rule:



Document Explorer must read from PostgreSQL through FastAPI. The frontend must not access the database directly.



### 7. System Health



Purpose:



System Health shows whether the retrieval platform is operational.



Expected functionality:



\- Show FastAPI health.

\- Show PostgreSQL connectivity.

\- Show OpenSearch connectivity.

\- Show Qdrant connectivity.

\- Show Redis connectivity.

\- Show worker heartbeat later.

\- Show recent system events later.

\- Show recent failed jobs.

\- Show current app mode.

\- Show service versions where practical.

\- Show clear degraded states.



Final rule:



System Health must not show fake uptime or fake service status. Unknown status should be shown as unknown.



## Core flows



### Flow 1: Ingestion



Purpose:



Load BEIR SciFact into PostgreSQL.



Expected steps:



1\. Download or load the SciFact dataset.

2\. Parse corpus documents.

3\. Parse benchmark queries.

4\. Parse qrels.

5\. Store documents in PostgreSQL.

6\. Chunk documents for retrieval.

7\. Store chunks in PostgreSQL.

8\. Store queries in PostgreSQL.

9\. Store qrels in PostgreSQL.

10\. Record ingestion job status.

11\. Record ingestion counts.

12\. Report success or failure.



Ingestion requirements:



\- Ingestion should be idempotent where practical.

\- Re-running ingestion should not create uncontrolled duplicates.

\- Document IDs from the dataset must be preserved.

\- Query IDs from the dataset must be preserved.

\- Qrels must preserve query to document relevance relationships.

\- Errors must be stored or logged clearly.

\- Ingestion should be visible in Index Console.



### Flow 2: BM25 index build



Purpose:



Build a lexical index in OpenSearch.



Expected steps:



1\. Read documents or chunks from PostgreSQL.

2\. Create a versioned OpenSearch index.

3\. Index searchable content.

4\. Store index version metadata in PostgreSQL.

5\. Mark index status as building, completed, or failed.

6\. Do not activate failed indexes.

7\. Allow explicit activation of a completed index later.



BM25 requirements:



\- OpenSearch is the source of BM25 retrieval.

\- BM25 must not be simulated with a simple database LIKE query.

\- Index versions must be tracked.

\- Build failures must be visible.

\- Active index state must come from backend state.



### Flow 3: Dense index build



Purpose:



Build a dense vector index in Qdrant.



Expected steps:



1\. Read chunks from PostgreSQL.

2\. Generate embeddings with BAAI/bge-small-en-v1.5.

3\. Create a versioned Qdrant collection.

4\. Upsert vectors into Qdrant.

5\. Store mapping between vector point IDs, chunk IDs, and document IDs.

6\. Store index version metadata in PostgreSQL.

7\. Mark index status as building, completed, or failed.

8\. Do not activate failed indexes.

9\. Allow explicit activation of a completed index later.



Dense retrieval requirements:



\- Qdrant is the source of dense retrieval.

\- Embeddings must use BAAI/bge-small-en-v1.5 unless explicitly changed.

\- Vector records must map back to chunks and documents.

\- Dense index version must be tracked.

\- Build failures must be visible.



### Flow 4: Search execution



Purpose:



Run a user query through one selected retrieval mode.



Expected steps:



1\. Receive query through FastAPI.

2\. Validate request with Pydantic.

3\. Create request ID and trace ID.

4\. Determine retrieval mode.

5\. Determine active index versions.

6\. Execute retrieval stage or stages.

7\. Fuse results if hybrid mode is selected.

8\. Rerank candidates if reranker mode is selected.

9\. Map chunk results back to documents.

10\. Deduplicate document-level results where required.

11\. Hydrate result details from PostgreSQL.

12\. Measure latency.

13\. Persist query trace.

14\. Return ranked results to frontend.



Search requirements:



\- FastAPI owns search orchestration.

\- The frontend must never directly call OpenSearch or Qdrant.

\- Results must include enough metadata to power Query Trace.

\- Search should support top k.

\- Search errors must be structured.

\- Search latency must be measured.



### Flow 5: Evaluation



Purpose:



Evaluate retrieval modes against SciFact qrels.



Expected steps:



1\. Select retrieval mode.

2\. Select index version or active indexes.

3\. Load evaluation query set.

4\. For each query, run retrieval.

5\. Map chunk results to document IDs.

6\. Deduplicate document IDs.

7\. Compare ranked documents against qrels.

8\. Compute Recall@5.

9\. Compute Recall@10.

10\. Compute MRR@10.

11\. Compute NDCG@10.

12\. Measure latency per query.

13\. Compute p50 latency.

14\. Compute p95 latency.

15\. Store evaluation run.

16\. Store per-query evaluation details where practical.

17\. Mark run as completed, failed, or partial.



Evaluation requirements:



\- Evaluation must use real qrels.

\- Chunk results must be converted to document IDs before scoring.

\- Document-level deduplication must happen before scoring.

\- Metrics must be computed consistently across retrieval modes.

\- Failed and partial runs must be visible.

\- Evaluation jobs should run as background jobs when expensive.



### Flow 6: Experiment comparison



Purpose:



Compare evaluation runs and retrieval configurations.



Expected steps:



1\. Load selected evaluation runs.

2\. Confirm run statuses.

3\. Compare quality metrics.

4\. Compare latency metrics.

5\. Compute deltas.

6\. Present tradeoffs in dashboard.



Experiment comparison requirements:



\- Comparisons must use stored evaluation runs.

\- The UI should not compare incomplete runs as if they are complete.

\- Metadata must make each run understandable.

\- Quality and latency should both be visible.



## Retrieval modes



### BM25



BM25 retrieval uses OpenSearch.



Inputs:



\- Query text

\- Active lexical index version

\- Top k



Outputs:



\- Ranked chunk or document candidates

\- BM25 scores

\- Rank positions

\- Latency



Purpose:



BM25 provides the lexical baseline.



### Dense



Dense retrieval uses Qdrant.



Inputs:



\- Query text

\- Query embedding generated with BAAI/bge-small-en-v1.5

\- Active vector index version

\- Top k



Outputs:



\- Ranked vector candidates

\- Similarity scores

\- Chunk IDs

\- Document IDs

\- Rank positions

\- Latency



Purpose:



Dense retrieval provides the semantic retrieval baseline.



### Hybrid RRF



Hybrid RRF combines BM25 and dense retrieval.



Inputs:



\- Query text

\- Active lexical index version

\- Active vector index version

\- BM25 candidate count

\- Dense candidate count

\- RRF settings

\- Top k



Outputs:



\- BM25 candidate list

\- Dense candidate list

\- Fused candidate list

\- RRF scores

\- Rank positions

\- Latency



Purpose:



Hybrid RRF tests whether combining lexical and semantic retrieval improves quality.



### Hybrid plus reranker



Hybrid plus reranker applies a cross-encoder to hybrid candidates.



Inputs:



\- Query text

\- Hybrid RRF candidate list

\- Candidate text

\- Reranker model cross-encoder/ms-marco-MiniLM-L-6-v2

\- Top k



Outputs:



\- Pre-rerank candidates

\- Reranked candidates

\- Reranker scores

\- Rank changes

\- Latency by retrieval and reranking stage



Purpose:



Hybrid plus reranker tests whether a more expensive second-stage model improves ranking quality.



## Expected high-level data model



The final database model should be designed in later steps, but the system is expected to include these conceptual entities.



### Dataset



Represents a benchmark dataset such as SciFact.



Likely fields:



\- id

\- name

\- version

\- source

\- created\_at



### Document



Represents a source document from the corpus.



Likely fields:



\- id

\- dataset\_id

\- external\_document\_id

\- title

\- text

\- metadata

\- created\_at



### Chunk



Represents a searchable chunk derived from a document.



Likely fields:



\- id

\- document\_id

\- chunk\_index

\- text

\- token\_count

\- metadata

\- created\_at



### Query



Represents a benchmark query.



Likely fields:



\- id

\- dataset\_id

\- external\_query\_id

\- text

\- metadata

\- created\_at



### Qrel



Represents a relevance judgment between a query and a document.



Likely fields:



\- id

\- query\_id

\- document\_id

\- relevance

\- created\_at



### IndexVersion



Represents a versioned lexical or vector index.



Likely fields:



\- id

\- dataset\_id

\- index\_type

\- version\_name

\- backend

\- status

\- is\_active

\- document\_count

\- chunk\_count

\- error\_message

\- created\_at

\- activated\_at



Index types may include:



\- lexical

\- vector



Statuses may include:



\- pending

\- building

\- completed

\- failed

\- active

\- archived



### SearchTrace



Represents a single search execution trace.



Likely fields:



\- id

\- trace\_id

\- request\_id

\- query\_text

\- retrieval\_mode

\- lexical\_index\_version\_id

\- vector\_index\_version\_id

\- reranker\_enabled

\- total\_latency\_ms

\- status

\- error\_message

\- created\_at



### SearchTraceStage



Represents a stage inside a search trace.



Likely fields:



\- id

\- search\_trace\_id

\- stage\_name

\- started\_at

\- completed\_at

\- latency\_ms

\- status

\- metadata

\- error\_message



### SearchResult



Represents ranked search results for a trace.



Likely fields:



\- id

\- search\_trace\_id

\- rank

\- document\_id

\- chunk\_id

\- bm25\_score

\- dense\_score

\- rrf\_score

\- reranker\_score

\- final\_score

\- metadata



### EvaluationRun



Represents a full evaluation job.



Likely fields:



\- id

\- dataset\_id

\- retrieval\_mode

\- lexical\_index\_version\_id

\- vector\_index\_version\_id

\- reranker\_enabled

\- status

\- query\_count

\- recall\_at\_5

\- recall\_at\_10

\- mrr\_at\_10

\- ndcg\_at\_10

\- p50\_latency\_ms

\- p95\_latency\_ms

\- error\_message

\- started\_at

\- completed\_at

\- created\_at



### EvaluationQueryResult



Represents per-query evaluation details.



Likely fields:



\- id

\- evaluation\_run\_id

\- query\_id

\- retrieved\_document\_ids

\- relevant\_document\_ids

\- recall\_at\_5

\- recall\_at\_10

\- reciprocal\_rank\_at\_10

\- ndcg\_at\_10

\- latency\_ms

\- metadata



### Job



Represents background work.



Likely fields:



\- id

\- job\_type

\- status

\- rq\_job\_id

\- idempotency\_key

\- started\_at

\- completed\_at

\- error\_message

\- metadata

\- created\_at



### SystemEvent



Represents notable system events.



Likely fields:



\- id

\- event\_type

\- severity

\- message

\- metadata

\- created\_at



## Expected API surface



The API should be versioned under:



\- /api/v1



The exact routes will be designed in implementation steps. The high-level surface should include the following groups.



### Health endpoints



Expected endpoints:



\- GET /api/v1/health

\- GET /api/v1/health/services



Purpose:



\- Check FastAPI health.

\- Check PostgreSQL connectivity.

\- Check OpenSearch connectivity.

\- Check Qdrant connectivity.

\- Check Redis connectivity.

\- Check worker heartbeat later.



### Dataset endpoints



Expected endpoints:



\- GET /api/v1/datasets

\- GET /api/v1/datasets/{dataset\_id}

\- GET /api/v1/datasets/{dataset\_id}/stats



Purpose:



\- Inspect loaded datasets.

\- View corpus, query, qrel, and chunk counts.



### Document endpoints



Expected endpoints:



\- GET /api/v1/documents

\- GET /api/v1/documents/{document\_id}

\- GET /api/v1/documents/{document\_id}/chunks

\- GET /api/v1/documents/{document\_id}/qrels



Purpose:



\- Power Document Explorer.

\- Support pagination and filtering.



### Query endpoints



Expected endpoints:



\- GET /api/v1/queries

\- GET /api/v1/queries/{query\_id}

\- GET /api/v1/queries/{query\_id}/qrels



Purpose:



\- Inspect benchmark queries and their relevance judgments.



### Search endpoints



Expected endpoints:



\- POST /api/v1/search

\- GET /api/v1/search/traces

\- GET /api/v1/search/traces/{trace\_id}



Purpose:



\- Execute retrieval.

\- Return ranked results.

\- Persist traces.

\- Power Search Lab and Query Trace.



### Evaluation endpoints



Expected endpoints:



\- POST /api/v1/evaluations

\- GET /api/v1/evaluations

\- GET /api/v1/evaluations/{evaluation\_run\_id}

\- GET /api/v1/evaluations/{evaluation\_run\_id}/query-results



Purpose:



\- Start evaluation jobs.

\- List evaluation runs.

\- Inspect evaluation metrics.

\- Inspect per-query evaluation details.



### Experiment comparison endpoints



Expected endpoints:



\- GET /api/v1/experiments/compare



Purpose:



\- Compare evaluation runs.

\- Compare modes.

\- Compare index versions.

\- Compare quality and latency tradeoffs.



### Index endpoints



Expected endpoints:



\- GET /api/v1/indexes

\- GET /api/v1/indexes/{index\_version\_id}

\- POST /api/v1/indexes/build

\- POST /api/v1/indexes/{index\_version\_id}/activate



Purpose:



\- Inspect index versions.

\- Build indexes.

\- Activate completed indexes.

\- Prevent failed indexes from auto-activating.



Admin protection:



\- Build and activate endpoints must later be protected by ADMIN\_API\_KEY or equivalent protection.



### Job endpoints



Expected endpoints:



\- GET /api/v1/jobs

\- GET /api/v1/jobs/{job\_id}



Purpose:



\- Inspect background job status.

\- Power Index Console and System Health.



### System event endpoints



Expected endpoints:



\- GET /api/v1/system/events



Purpose:



\- Show recent system events.

\- Support system debugging and observability.



## API design requirements



General requirements:



\- FastAPI owns all backend logic.

\- Pydantic validates requests and responses.

\- SQLAlchemy owns database access.

\- Alembic owns migrations.

\- List endpoints should support pagination.

\- List endpoints should support useful filtering.

\- Responses should be structured and predictable.

\- Errors should be structured.

\- Expensive admin actions must later require ADMIN\_API\_KEY.

\- The frontend must not directly access the database, OpenSearch, or Qdrant.

\- API responses should include trace IDs, request IDs, job IDs, and timestamps where relevant.



## Evaluation metrics



Aletheia must support the following final metrics.



### Recall@5



Measures whether relevant documents appear in the top 5 retrieved document results.



Rule:



\- Compute after mapping chunks to document IDs.

\- Compute after document-level deduplication.



### Recall@10



Measures whether relevant documents appear in the top 10 retrieved document results.



Rule:



\- Compute after mapping chunks to document IDs.

\- Compute after document-level deduplication.



### MRR@10



Mean Reciprocal Rank at 10.



Rule:



\- Find the rank of the first relevant document in the top 10.

\- Use reciprocal rank.

\- Use 0 if no relevant document appears in the top 10.



### NDCG@10



Normalized Discounted Cumulative Gain at 10.



Rule:



\- Use relevance judgments from qrels.

\- Compute at document level.

\- Use deduplicated ranked document IDs.



### p50 latency



Median query latency.



Rule:



\- Compute from measured query execution latency.



### p95 latency



95th percentile query latency.



Rule:



\- Compute from measured query execution latency.



## Query tracing requirements



Query traces are central to Aletheia.



Each search request should eventually produce a trace containing:



\- trace\_id

\- request\_id

\- query text

\- retrieval mode

\- active index versions

\- reranker setting

\- stage timings

\- candidate lists

\- score fields

\- rank positions

\- rank changes

\- chunk IDs

\- document IDs

\- final returned results

\- errors if present

\- created timestamp



Trace stages should make the retrieval pipeline understandable.



For hybrid plus reranker, traces should show:



\- BM25 candidates

\- Dense candidates

\- RRF fused candidates

\- Reranker candidates

\- Final reranked output

\- Rank changes from fusion to reranking

\- Latency added by reranking



Final rule:



Trace data must be stored by the backend. The frontend should display traces, not invent them.



## Experiment comparison requirements



Experiment comparison should help answer:



\- Which retrieval mode performs best?

\- Which retrieval mode is fastest?

\- How much quality does hybrid retrieval add?

\- How much quality does reranking add?

\- How much latency does reranking add?

\- Which index version is active?

\- Which index version performed best?

\- Which evaluation runs are comparable?



Comparison view should show:



\- Retrieval mode

\- Dataset

\- Index version

\- Reranker setting

\- Query count

\- Recall@5

\- Recall@10

\- MRR@10

\- NDCG@10

\- p50 latency

\- p95 latency

\- Run status

\- Run timestamp



Final rule:



Do not compare fake runs. Do not compare incomplete runs as if they are complete.



## System health requirements



System Health should report real backend status.



Services to check:



\- FastAPI

\- PostgreSQL

\- OpenSearch

\- Qdrant

\- Redis

\- RQ worker later



Health states may include:



\- healthy

\- degraded

\- unavailable

\- unknown



System Health should also eventually show:



\- active app mode

\- active lexical index

\- active vector index

\- recent failed jobs

\- recent system events

\- worker heartbeat

\- last successful evaluation run

\- last successful index build



Final rule:



Unknown service status is better than fake healthy status.



## Deployment direction



### Local development



Local development should use:



\- Docker Compose

\- Docker Postgres

\- Redis

\- OpenSearch

\- Qdrant

\- FastAPI

\- Next.js



Windows 11 friendliness matters. Setup instructions should be PowerShell-compatible where practical.



### Hosted database



Hosted PostgreSQL should use:



\- Neon Postgres



The project should not rely on Supabase-specific backend features.



### Public frontend



The public frontend may later be deployed with:



\- Vercel



Public domain later:



\- aletheia.yuvrajkashyap.com



### Backend hosting



Backend hosting will be decided later.



The backend must remain FastAPI-owned regardless of hosting choice.



### CI



CI may later use:



\- GitHub Actions



CI should eventually validate:



\- Backend tests

\- Frontend build

\- Linting

\- Type checking

\- Migration checks where practical



## App modes



Aletheia should eventually support three modes.



### Local mode



Purpose:



\- Full local development.

\- Local services through Docker Compose.

\- Safe for development and testing.



### Demo mode



Purpose:



\- Public demo with real data.

\- Restricted admin actions.

\- Precomputed real indexes and evaluations allowed.

\- No fake system state.



### Production mode



Purpose:



\- More secure deployed environment.

\- Protected admin actions.

\- No exposed secrets.

\- Clear operational status.



## Admin safety requirements



Administrative and expensive actions must later be protected.



Protected actions include:



\- Dataset ingestion

\- BM25 index build

\- Dense index build

\- Index activation

\- Full evaluation runs

\- Retry failed expensive jobs

\- Destructive reset actions if ever added



Protection method later:



\- ADMIN\_API\_KEY or equivalent



Final rule:



Public users should not be able to trigger expensive backend work.



## Implementation principles



Aletheia should be built in clear phases.



Principles:



\- Build architecture before polish.

\- Keep retrieval correctness ahead of UI cosmetics.

\- Prefer real data over impressive-looking placeholders.

\- Keep backend orchestration in FastAPI.

\- Keep frontend as a client of backend APIs.

\- Store enough metadata to debug and compare runs.

\- Make failure states visible.

\- Keep Windows 11 setup practical.

\- Keep every endpoint and page tied to the retrieval platform identity.



## Final done definition



Aletheia is done only when:



\- BEIR SciFact ingestion works.

\- Documents are stored in PostgreSQL.

\- Chunks are stored in PostgreSQL.

\- Queries are stored in PostgreSQL.

\- Qrels are stored in PostgreSQL.

\- BM25 retrieval works through OpenSearch.

\- Dense retrieval works through Qdrant.

\- Embeddings use BAAI/bge-small-en-v1.5.

\- Hybrid RRF works.

\- Reranking works with cross-encoder/ms-marco-MiniLM-L-6-v2.

\- Search Lab can run real searches.

\- Query Trace can inspect real traces.

\- Evaluation Dashboard shows real evaluation metrics.

\- Experiment Comparison compares real runs.

\- Index Console shows real index and job state.

\- Document Explorer shows real corpus data.

\- System Health shows real service status.

\- Evaluation maps chunk results back to document IDs.

\- Evaluation deduplicates document IDs before scoring.

\- Recall@5 is computed correctly.

\- Recall@10 is computed correctly.

\- MRR@10 is computed correctly.

\- NDCG@10 is computed correctly.

\- p50 latency is measured from real runs.

\- p95 latency is measured from real runs.

\- Indexes are versioned.

\- Failed indexes never auto-activate.

\- Admin actions are protected before public exposure.

\- The final dashboard contains no fake metrics.

\- The project can be run locally with clear Windows 11 friendly instructions.

\- The codebase is credible for a serious technical portfolio review.


