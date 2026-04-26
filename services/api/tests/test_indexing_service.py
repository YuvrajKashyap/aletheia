from types import SimpleNamespace
from uuid import UUID

from app.indexing import statuses
from app.indexing.service import (
    create_index_version,
    generate_index_version_name,
    generate_lexical_index_name,
    generate_vector_collection_name,
    safe_name,
)


DATASET_ID = UUID("00000000-0000-0000-0000-000000000002")


class FakeCreateIndexVersionDb:
    def __init__(self, existing):
        self.dataset = SimpleNamespace(id=DATASET_ID, name="beir/scifact", version="test")
        self.existing = existing
        self.added = []
        self.scalar_calls = 0

    def get(self, model, object_id):
        return self.dataset if object_id == DATASET_ID else None

    def scalar(self, statement):
        self.scalar_calls += 1
        if self.scalar_calls == 1:
            return 5183
        if self.scalar_calls == 2:
            return 5183
        return self.existing

    def add(self, value):
        self.added.append(value)

    def commit(self):
        return None

    def refresh(self, value):
        return None


def existing_index_version(status: str, is_active: bool = False):
    return SimpleNamespace(
        dataset_id=DATASET_ID,
        name="beir-scifact-test-scifact-document-v1-1-0",
        status=status,
        is_active=is_active,
        activated_at="2026-04-25T00:00:00Z" if is_active else None,
        lexical_index_name="aletheia-lexical-existing",
        vector_collection_name="aletheia-vector-existing",
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_dimension=384,
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        document_count=0,
        chunk_count=0,
        vector_count=0,
        config_json={"existing": True},
        notes="old notes",
    )


def test_generated_index_version_name_is_deterministic() -> None:
    first = generate_index_version_name(
        "beir/scifact",
        "test",
        "scifact_document_v1",
        "1.0",
        "BAAI/bge-small-en-v1.5",
    )
    second = generate_index_version_name(
        "beir/scifact",
        "test",
        "scifact_document_v1",
        "1.0",
        "BAAI/bge-small-en-v1.5",
    )

    assert first == second


def test_generated_names_are_lowercase_and_safe() -> None:
    name = generate_index_version_name(
        "BEIR/SciFact",
        "Test Split",
        "SciFact Document V1",
        "1.0",
        "BAAI/bge-small-en-v1.5",
    )

    assert name == name.lower()
    assert "/" not in name
    assert " " not in name


def test_safe_name_replaces_unsafe_characters() -> None:
    assert safe_name("BEIR/SciFact test") == "beir-scifact-test"


def test_lexical_name_includes_dataset_and_chunking_info() -> None:
    name = generate_lexical_index_name("beir/scifact", "test", "scifact_document_v1", "1.0")

    assert name.startswith("aletheia-lexical-")
    assert "beir-scifact" in name
    assert "scifact-document-v1" in name


def test_vector_collection_name_includes_dataset_chunking_and_model_info() -> None:
    name = generate_vector_collection_name(
        "beir/scifact",
        "test",
        "scifact_document_v1",
        "1.0",
        "BAAI/bge-small-en-v1.5",
    )

    assert name.startswith("aletheia-vector-")
    assert "beir-scifact" in name
    assert "bge-small-en-v1-5" in name


def test_status_transition_sets_are_metadata_only() -> None:
    assert statuses.READY in statuses.ACTIVATABLE_STATUSES
    assert statuses.ACTIVE not in statuses.NON_ACTIVE_STATUSES


def test_create_existing_ready_index_version_preserves_lifecycle_status() -> None:
    existing = existing_index_version(statuses.READY)
    db = FakeCreateIndexVersionDb(existing)

    result = create_index_version(
        db,
        DATASET_ID,
        name=existing.name,
        notes="updated notes",
        config_json={"api": True},
    )

    assert result is existing
    assert result.status == statuses.READY
    assert result.is_active is False
    assert result.activated_at is None
    assert result.notes == "updated notes"
    assert result.config_json == {"existing": True, "api": True}
    assert result.document_count == 5183
    assert result.chunk_count == 5183


def test_create_existing_active_index_version_preserves_active_lifecycle() -> None:
    existing = existing_index_version(statuses.ACTIVE, is_active=True)
    original_activated_at = existing.activated_at
    db = FakeCreateIndexVersionDb(existing)

    result = create_index_version(
        db,
        DATASET_ID,
        name=existing.name,
        status=statuses.PENDING,
    )

    assert result is existing
    assert result.status == statuses.ACTIVE
    assert result.is_active is True
    assert result.activated_at == original_activated_at
    assert result.lexical_index_name == "aletheia-lexical-existing"
    assert result.vector_collection_name == "aletheia-vector-existing"
