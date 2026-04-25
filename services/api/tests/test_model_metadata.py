from sqlalchemy import Index, UniqueConstraint

import app.models  # noqa: F401
from app.db.base import Base


EXPECTED_TABLE_NAMES = {
    "datasets",
    "documents",
    "chunks",
    "benchmark_queries",
    "relevance_judgments",
    "ingestion_runs",
    "index_versions",
    "index_jobs",
    "queries",
    "query_traces",
    "retrieval_candidates",
    "saved_queries",
    "query_replays",
    "experiment_configs",
    "evaluation_runs",
    "evaluation_query_results",
    "evaluation_reports",
    "system_events",
    "worker_heartbeats",
}


def unique_column_sets(table_name: str) -> set[tuple[str, ...]]:
    table = Base.metadata.tables[table_name]
    return {
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def table_indexes(table_name: str) -> set[Index]:
    return Base.metadata.tables[table_name].indexes


def test_expected_core_tables_are_registered() -> None:
    assert EXPECTED_TABLE_NAMES.issubset(Base.metadata.tables.keys())


def test_important_constraints_and_indexes_are_registered() -> None:
    assert ("name", "version") in unique_column_sets("datasets")
    assert ("dataset_id", "external_id") in unique_column_sets("documents")
    assert ("query_id",) in unique_column_sets("query_traces")
    assert ("name",) in unique_column_sets("experiment_configs")

    active_dataset_indexes = [
        index
        for index in table_indexes("index_versions")
        if index.name == "uq_index_versions_active_dataset"
    ]

    assert len(active_dataset_indexes) == 1

    active_dataset_index = active_dataset_indexes[0]
    assert active_dataset_index.unique is True
    assert [column.name for column in active_dataset_index.columns] == ["dataset_id"]
    assert active_dataset_index.dialect_options["postgresql"]["where"] is not None
