from app.indexing import statuses
from app.indexing.service import (
    generate_index_version_name,
    generate_lexical_index_name,
    generate_vector_collection_name,
    safe_name,
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
