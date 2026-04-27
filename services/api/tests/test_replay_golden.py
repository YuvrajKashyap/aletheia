from types import SimpleNamespace
from uuid import UUID

from app.replay.golden import (
    DEFAULT_GOLDEN_QUERY_SOURCE,
    build_saved_query_metadata_from_benchmark_query,
    get_default_golden_query_limit,
)


class FakeScalars:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class FakeDb:
    def __init__(self, judgments):
        self.judgments = judgments

    def scalars(self, statement):
        return FakeScalars(self.judgments)


def test_default_source_name_and_limit() -> None:
    assert DEFAULT_GOLDEN_QUERY_SOURCE == "golden_scifact"
    assert get_default_golden_query_limit() == 20


def test_metadata_builder_uses_qrel_derived_ids() -> None:
    benchmark_query = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        external_id="q1",
    )
    dataset = SimpleNamespace(name="beir/scifact", version="test")
    judgments = [
        SimpleNamespace(
            document_id=UUID("00000000-0000-0000-0000-000000000010"),
            document_external_id="doc-10",
        )
    ]

    metadata = build_saved_query_metadata_from_benchmark_query(
        FakeDb(judgments),
        benchmark_query,
        dataset,
    )

    assert metadata["source"] == "golden_scifact"
    assert metadata["query_external_id"] == "q1"
    assert metadata["relevant_document_ids"] == ["00000000-0000-0000-0000-000000000010"]
    assert metadata["relevant_document_external_ids"] == ["doc-10"]
    assert metadata["relevance_count"] == 1
