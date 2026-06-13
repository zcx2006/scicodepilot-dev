from __future__ import annotations

import pytest

from scicodepilot.memory.record import FailureMemoryRecord
from scicodepilot.memory.store import FailureMemoryStore


def make_record(record_id: str = "record_1") -> FailureMemoryRecord:
    return FailureMemoryRecord(
        record_id=record_id,
        task_id="task_1",
        error_type="tensor_shape",
        failure_category="source_code",
        command="python train.py",
        exception_type="RuntimeError",
        error_message="mat1 and mat2 shapes cannot be multiplied",
        traceback_summary="shape mismatch",
        root_cause_hypothesis="classifier input dimension is wrong",
        repair_action="align classifier dimension",
        patch_plan_summary="change classifier_expected_dim from 128 to 64",
        verification_success=True,
        score=1.0,
        created_from="test",
        metadata={"suite": "unit"},
    )


def test_failure_memory_record_rejects_empty_record_id() -> None:
    with pytest.raises(ValueError, match="record_id must be non-empty"):
        FailureMemoryRecord(record_id="")


def test_jsonl_save_load_round_trip(tmp_path) -> None:
    path = tmp_path / "memory.jsonl"
    store = FailureMemoryStore([make_record()])

    store.save_jsonl(path)
    loaded = FailureMemoryStore.load_jsonl(path)

    assert loaded.all_records() == [make_record()]


def test_append_and_all_records() -> None:
    store = FailureMemoryStore()
    record = make_record()

    store.append(record)

    assert store.all_records() == [record]


def test_empty_store_retrieval_returns_empty_list() -> None:
    assert FailureMemoryStore().retrieve("tensor shape", top_k=3) == []


def test_missing_jsonl_loads_empty_store(tmp_path) -> None:
    store = FailureMemoryStore.load_jsonl(tmp_path / "missing.jsonl")

    assert store.all_records() == []


def test_malformed_jsonl_raises_clear_value_error(tmp_path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"record_id": "ok"}\n{bad json}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="line 2"):
        FailureMemoryStore.load_jsonl(path)
