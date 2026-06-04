from __future__ import annotations

from scicodepilot.llm.memory_prompt_builder import build_memory_augmented_patch_prompt
from scicodepilot.memory.record import FailureMemoryRecord, RetrievedFailureMemory


def make_record(record_id: str) -> FailureMemoryRecord:
    return FailureMemoryRecord(
        record_id=record_id,
        task_id="repair_tensor_shape_001",
        error_type="tensor_shape",
        failure_category="source_code",
        command="python train.py",
        exception_type="RuntimeError",
        error_message="mat1 and mat2 shapes cannot be multiplied",
        traceback_summary="shape mismatch",
        root_cause_hypothesis="downstream dimension mismatch",
        repair_action="align dimensions",
        patch_plan_summary="change classifier_expected_dim",
        verification_success=True,
        score=1.0,
        created_from="test",
        metadata={},
    )


def test_memory_prompt_includes_safety_constraints_and_patchplan_json_requirement() -> None:
    prompt = build_memory_augmented_patch_prompt(make_record("query"), [])

    assert "Return only structured PatchPlan JSON" in prompt
    assert "no shell execution" in prompt
    assert "no dependency installation" in prompt
    assert "no fake data creation" in prompt
    assert "no absolute paths" in prompt
    assert "no path traversal" in prompt
    assert "no benchmark/test/output modification" in prompt
    assert "patch must still pass PatchSafetyReviewer" in prompt


def test_memory_prompt_includes_retrieved_examples() -> None:
    retrieved = [
        RetrievedFailureMemory(
            record=make_record("memory_1"),
            score=1.5,
            matched_terms=["tensor_shape", "mat1"],
        )
    ]

    prompt = build_memory_augmented_patch_prompt(make_record("query"), retrieved)

    assert "Example 1:" in prompt
    assert "memory_1" in prompt
    assert "retrieval_score: 1.5" in prompt
    assert "matched_terms: tensor_shape, mat1" in prompt
