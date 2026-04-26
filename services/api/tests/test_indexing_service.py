from types import SimpleNamespace
from uuid import UUID

import pytest

from app.indexing import statuses
from app.indexing.service import (
    activate_index_version,
    create_index_version,
    generate_index_version_name,
    generate_lexical_index_name,
    generate_vector_collection_name,
    rollback_to_index_version,
    safe_name,
)


DATASET_ID = UUID("00000000-0000-0000-0000-000000000002")
ACTIVE_INDEX_ID = UUID("10000000-0000-0000-0000-000000000001")
READY_INDEX_ID = UUID("10000000-0000-0000-0000-000000000002")


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
        id=ACTIVE_INDEX_ID if is_active else READY_INDEX_ID,
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
        updated_at=None,
    )


class FakeScalarResult:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class FakeActivationDb:
    def __init__(self, target, current_versions, fail_on_flush: bool = False):
        self.target = target
        self.current_versions = current_versions
        self.fail_on_flush = fail_on_flush
        self.flush_count = 0
        self.commit_count = 0
        self.rollback_count = 0

    def get(self, model, object_id):
        if object_id == self.target.id:
            return self.target
        for current in self.current_versions:
            if object_id == current.id:
                return current
        return None

    def scalars(self, statement):
        return FakeScalarResult(self.current_versions)

    def flush(self):
        self.flush_count += 1
        assert all(not current.is_active for current in self.current_versions)
        if self.fail_on_flush:
            raise RuntimeError("flush failed")

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def refresh(self, value):
        return None


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


def test_activate_ready_second_version_deprecates_previous_active_before_target() -> None:
    previous = existing_index_version(statuses.ACTIVE, is_active=True)
    target = existing_index_version(statuses.READY)
    target.id = READY_INDEX_ID
    db = FakeActivationDb(target, [previous])

    result = activate_index_version(db, target.id)

    assert result is target
    assert previous.status == statuses.DEPRECATED
    assert previous.is_active is False
    assert previous.updated_at is not None
    assert target.status == statuses.ACTIVE
    assert target.is_active is True
    assert target.activated_at is not None
    assert target.updated_at == target.activated_at
    assert sum(1 for version in [previous, target] if version.is_active) == 1
    assert db.flush_count == 1
    assert db.commit_count == 1
    assert db.rollback_count == 0


def test_rollback_to_index_version_uses_safe_activation_transition() -> None:
    current = existing_index_version(statuses.ACTIVE, is_active=True)
    rollback_target = existing_index_version(statuses.DEPRECATED)
    rollback_target.id = READY_INDEX_ID
    db = FakeActivationDb(rollback_target, [current])

    result = rollback_to_index_version(db, rollback_target.id)

    assert result is rollback_target
    assert current.status == statuses.DEPRECATED
    assert current.is_active is False
    assert rollback_target.status == statuses.ACTIVE
    assert rollback_target.is_active is True
    assert sum(1 for version in [current, rollback_target] if version.is_active) == 1
    assert db.flush_count == 1


def test_activate_already_active_index_version_is_idempotent() -> None:
    target = existing_index_version(statuses.ACTIVE, is_active=True)
    db = FakeActivationDb(target, [])

    result = activate_index_version(db, target.id)

    assert result is target
    assert result.status == statuses.ACTIVE
    assert result.is_active is True
    assert db.flush_count == 0
    assert db.commit_count == 0


def test_activation_failure_rolls_back_session() -> None:
    previous = existing_index_version(statuses.ACTIVE, is_active=True)
    target = existing_index_version(statuses.READY)
    target.id = READY_INDEX_ID
    db = FakeActivationDb(target, [previous], fail_on_flush=True)

    with pytest.raises(RuntimeError, match="flush failed"):
        activate_index_version(db, target.id)

    assert db.rollback_count == 1
    assert db.commit_count == 0
