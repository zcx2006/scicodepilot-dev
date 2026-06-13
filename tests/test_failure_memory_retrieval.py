from __future__ import annotations

from scicodepilot.memory.record import FailureMemoryRecord
from scicodepilot.memory.store import FailureMemoryStore


def record(
    record_id: str,
    error_type: str,
    message: str,
    category: str = "source_code",
    exception_type: str = "RuntimeError",
) -> FailureMemoryRecord:
    return FailureMemoryRecord(
        record_id=record_id,
        task_id=record_id,
        error_type=error_type,
        failure_category=category,
        command="python train.py",
        exception_type=exception_type,
        error_message=message,
        traceback_summary=message,
        root_cause_hypothesis=message,
        repair_action=message,
        patch_plan_summary=message,
        verification_success=True,
        score=1.0,
        created_from="test",
        metadata={},
    )


def test_tensor_shape_query_retrieves_tensor_shape_before_unrelated_records() -> None:
    store = FailureMemoryStore(
        [
            record("b_dtype", "dtype_mismatch", "float64 dtype mismatch"),
            record("a_shape", "tensor_shape", "mat1 and mat2 shapes cannot be multiplied"),
        ]
    )
    query = record(
        "query",
        "tensor_shape",
        "RuntimeError mat1 and mat2 shapes cannot be multiplied",
    )

    retrieved = store.retrieve(query, top_k=2)

    assert retrieved[0].record.record_id == "a_shape"
    assert retrieved[0].score > retrieved[1].score


def test_missing_module_query_retrieves_dependency_memory() -> None:
    store = FailureMemoryStore(
        [
            record("source", "tensor_shape", "shape mismatch"),
            record(
                "dependency",
                "missing_module",
                "No module named sklearn_extra",
                category="env_data",
                exception_type="ModuleNotFoundError",
            ),
        ]
    )
    query = record(
        "query",
        "missing_module",
        "ModuleNotFoundError No module named sklearn_extra",
        category="env_data",
        exception_type="ModuleNotFoundError",
    )

    retrieved = store.retrieve(query, top_k=1)

    assert retrieved[0].record.record_id == "dependency"
    assert "sklearn_extra" in retrieved[0].matched_terms


def test_retrieval_tie_breaking_is_stable_by_record_id() -> None:
    store = FailureMemoryStore(
        [
            record("b_record", "tensor_shape", "same text"),
            record("a_record", "tensor_shape", "same text"),
        ]
    )

    retrieved = store.retrieve("same text", top_k=2)

    assert [item.record.record_id for item in retrieved] == ["a_record", "b_record"]
