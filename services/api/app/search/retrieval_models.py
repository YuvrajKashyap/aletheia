from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class LexicalSearchResult:
    rank: int
    chunk_id: str
    document_id: str | None
    dataset_id: str | None
    document_external_id: str | None
    chunk_external_id: str | None
    title: str | None
    text: str
    score: float
    token_count: int | None
    content_hash: str | None
    chunking_strategy: str | None
    chunking_version: str | None
    metadata_json: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class LexicalSearchResponse:
    query: str
    index_version_id: str | None
    index_name: str
    retrieval_mode: str = "bm25"
    top_k: int = 10
    total_hits: int | None = None
    results: list[LexicalSearchResult] = field(default_factory=list)
    latency_ms: float = 0.0

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["results"] = [result.to_dict() for result in self.results]
        return payload


@dataclass(frozen=True)
class DenseSearchResult:
    rank: int
    chunk_id: str
    document_id: str | None
    dataset_id: str | None
    index_version_id: str | None
    document_external_id: str | None
    chunk_external_id: str | None
    title: str | None
    text: str
    score: float
    token_count: int | None
    content_hash: str | None
    chunking_strategy: str | None
    chunking_version: str | None
    metadata_json: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DenseSearchResponse:
    query: str
    index_version_id: str | None
    collection_name: str
    retrieval_mode: str = "dense"
    top_k: int = 10
    total_hits: int | None = None
    query_embedding_dimension: int | None = None
    results: list[DenseSearchResult] = field(default_factory=list)
    latency_ms: float = 0.0
    embedding_latency_ms: float | None = None
    qdrant_latency_ms: float | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["results"] = [result.to_dict() for result in self.results]
        return payload
