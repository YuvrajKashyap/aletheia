from collections import namedtuple

from app.datasets.scifact import (
    SciFactLoadSummary,
    document_from_ir_record,
    load_scifact_to_db,
    qrel_from_ir_record,
    query_from_ir_record,
)


def test_document_record_conversion_handles_missing_optional_fields() -> None:
    FakeDoc = namedtuple("FakeDoc", ["doc_id", "text"])
    record = document_from_ir_record(FakeDoc("doc-1", "Document text"), "beir/scifact")

    assert record.external_id == "doc-1"
    assert record.title is None
    assert record.text == "Document text"
    assert record.source_url is None
    assert record.metadata_json["source_dataset_id"] == "beir/scifact"


def test_query_record_conversion_preserves_split_and_text() -> None:
    FakeQuery = namedtuple("FakeQuery", ["query_id", "text"])
    record = query_from_ir_record(FakeQuery("q-1", "Query text"), "beir/scifact/test", "test")

    assert record.external_id == "q-1"
    assert record.text == "Query text"
    assert record.split == "test"
    assert record.metadata_json["source_dataset_id"] == "beir/scifact/test"


def test_qrel_record_conversion_uses_document_level_ids() -> None:
    FakeQrel = namedtuple("FakeQrel", ["query_id", "doc_id", "relevance"])
    record = qrel_from_ir_record(FakeQrel("q-1", "doc-1", 2), "beir/scifact/test", "test")

    assert record.query_external_id == "q-1"
    assert record.document_external_id == "doc-1"
    assert record.relevance_score == 2.0


def test_summary_to_dict_serializes_expected_fields() -> None:
    summary = SciFactLoadSummary(documents_seen=1, queries_seen=2, qrels_seen=3, dry_run=True)

    payload = summary.to_dict()

    assert payload["documents_seen"] == 1
    assert payload["queries_seen"] == 2
    assert payload["qrels_seen"] == 3
    assert payload["dataset_id"] is None
    assert payload["dry_run"] is True


def test_dry_run_load_uses_iterators_without_writing(monkeypatch) -> None:
    class FakeDb:
        rolled_back = False

        def scalar(self, statement):
            return None

        def rollback(self) -> None:
            self.rolled_back = True

    monkeypatch.setattr(
        "app.datasets.scifact.iter_scifact_documents",
        lambda limit=None: [
            document_from_ir_record(
                namedtuple("FakeDoc", ["doc_id", "text"])("doc-1", "Document text"),
                "beir/scifact",
            )
        ],
    )
    monkeypatch.setattr(
        "app.datasets.scifact.iter_scifact_queries",
        lambda split="test", limit=None: [
            query_from_ir_record(
                namedtuple("FakeQuery", ["query_id", "text"])("q-1", "Query text"),
                "beir/scifact/test",
                split,
            )
        ],
    )
    monkeypatch.setattr(
        "app.datasets.scifact.iter_scifact_qrels",
        lambda split="test", limit=None: [
            qrel_from_ir_record(
                namedtuple("FakeQrel", ["query_id", "doc_id", "relevance"])("q-1", "doc-1", 1),
                "beir/scifact/test",
                split,
            )
        ],
    )

    db = FakeDb()
    summary = load_scifact_to_db(db, dry_run=True)

    assert summary.documents_seen == 1
    assert summary.queries_seen == 1
    assert summary.qrels_seen == 1
    assert summary.qrels_loaded == 1
    assert db.rolled_back is True
