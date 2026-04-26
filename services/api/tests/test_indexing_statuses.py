from app.indexing import statuses


def test_index_status_constants() -> None:
    assert statuses.PENDING == "pending"
    assert statuses.BUILDING == "building"
    assert statuses.READY == "ready"
    assert statuses.ACTIVE == "active"
    assert statuses.FAILED == "failed"
    assert statuses.DEPRECATED == "deprecated"


def test_index_status_sets() -> None:
    assert statuses.BUILDABLE_STATUSES == {"pending"}
    assert statuses.ACTIVATABLE_STATUSES == {"ready"}
    assert statuses.TERMINAL_STATUSES == {"failed", "deprecated"}
    assert statuses.NON_ACTIVE_STATUSES == {
        "pending",
        "building",
        "ready",
        "failed",
        "deprecated",
    }
