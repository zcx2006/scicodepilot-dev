import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.suite_result import BenchmarkCaseResult
from scicodepilot.eval.suite_runner import BenchmarkSuiteRunner, summarize_results
from scicodepilot.eval.task_loader import load_benchmark_task


ALL_TASK_IDS = [
    "repair_tensor_shape_001",
    "repair_dtype_mismatch_002",
    "repair_missing_module_003",
    "repair_missing_file_004",
    "repair_entrypoint_error_005",
    "repair_label_shape_006",
    "repair_device_mismatch_007",
    "repair_loss_input_008",
    "repair_collate_fn_009",
    "repair_config_key_010",
]


@pytest.mark.asyncio
async def test_suite_runner_diagnosis_missing_module_only() -> None:
    task = load_benchmark_task("benchmark/tasks/repair_missing_module_003")

    results = await BenchmarkSuiteRunner().run_tasks([task], mode="diagnosis")

    assert len(results) == 1
    assert results[0].parsed_error_type == "missing_module"
    assert results[0].diagnosis_passed is True


def test_summarize_results_counts_correctly() -> None:
    results = [
        BenchmarkCaseResult(
            task_id="a",
            mode="repair",
            diagnosis_passed=True,
            patch_plan_generated=True,
            patch_applied=True,
            verification_success=True,
            score=1.0,
            message="ok",
        ),
        BenchmarkCaseResult(
            task_id="b",
            mode="repair",
            diagnosis_passed=False,
            patch_plan_generated=True,
            patch_applied=False,
            verification_success=False,
            message="needs approval",
        ),
        BenchmarkCaseResult(
            task_id="c",
            mode="repair",
            message="no plan",
        ),
    ]

    summary = summarize_results(results, mode="repair")

    assert summary.total_tasks == 3
    assert summary.diagnosis_pass_count == 1
    assert summary.patch_plan_count == 2
    assert summary.patch_review_count == 0
    assert summary.patch_review_blocked_count == 0
    assert summary.patch_applied_count == 1
    assert summary.verification_success_count == 1
    assert summary.scored_task_count == 1
    assert summary.env_repair_plan_count == 0
    assert summary.total_score == 1.0
    assert summary.average_score == 1.0


@pytest.mark.asyncio
async def test_suite_runner_repair_default_does_not_apply_missing_module() -> None:
    task = load_benchmark_task("benchmark/tasks/repair_missing_module_003")

    results = await BenchmarkSuiteRunner().run_tasks([task], mode="repair")

    assert len(results) == 1
    assert results[0].patch_applied is False
    assert results[0].env_repair_plan_generated is True
    assert results[0].env_issue_category == "dependency"


@pytest.mark.asyncio
async def test_suite_runner_diagnosis_all_ten_tasks_pass() -> None:
    pytest.importorskip("torch")
    tasks = [
        load_benchmark_task(Path("benchmark/tasks") / task_id)
        for task_id in ALL_TASK_IDS
    ]

    results = await BenchmarkSuiteRunner().run_tasks(tasks, mode="diagnosis")
    summary = summarize_results(results, mode="diagnosis")

    assert len(results) == 10
    assert summary.diagnosis_pass_count == 10


@pytest.mark.asyncio
async def test_suite_runner_repair_confirm_apply_repairs_supported_tasks() -> None:
    pytest.importorskip("torch")
    tasks = [
        load_benchmark_task(Path("benchmark/tasks") / task_id)
        for task_id in ALL_TASK_IDS
    ]

    results = await BenchmarkSuiteRunner().run_tasks(
        tasks,
        mode="repair",
        confirm_apply=True,
    )
    by_task_id = {result.task_id: result for result in results}
    summary = summarize_results(results, mode="repair")

    assert by_task_id["repair_tensor_shape_001"].verification_success is True
    assert by_task_id["repair_dtype_mismatch_002"].verification_success is True
    assert by_task_id["repair_entrypoint_error_005"].verification_success is True
    assert by_task_id["repair_label_shape_006"].verification_success is True
    assert by_task_id["repair_device_mismatch_007"].verification_success is True
    assert by_task_id["repair_loss_input_008"].verification_success is True
    assert by_task_id["repair_collate_fn_009"].verification_success is True
    assert by_task_id["repair_config_key_010"].verification_success is True
    assert by_task_id["repair_missing_module_003"].patch_applied is False
    assert by_task_id["repair_missing_file_004"].patch_applied is False
    assert by_task_id["repair_missing_module_003"].env_repair_plan_generated is True
    assert by_task_id["repair_missing_file_004"].env_repair_plan_generated is True
    assert summary.total_tasks == 10
    assert summary.patch_plan_count == 8
    assert summary.patch_review_count == 8
    assert summary.patch_review_blocked_count == 0
    assert summary.patch_applied_count == 8
    assert summary.verification_success_count == 8
    assert summary.scored_task_count == 8
    assert summary.env_repair_plan_count == 2
    assert summary.average_score == 1.0
    assert all(
        by_task_id[task_id].score == 1.0
        for task_id in [
            "repair_tensor_shape_001",
            "repair_dtype_mismatch_002",
            "repair_entrypoint_error_005",
            "repair_label_shape_006",
            "repair_device_mismatch_007",
            "repair_loss_input_008",
            "repair_collate_fn_009",
            "repair_config_key_010",
        ]
    )


@pytest.mark.asyncio
async def test_suite_runner_repair_confirm_apply_with_mock_llm_provider(monkeypatch) -> None:
    pytest.importorskip("torch")
    monkeypatch.setenv("SCICODEPILOT_LLM_PROVIDER", "mock")
    tasks = [
        load_benchmark_task(Path("benchmark/tasks") / task_id)
        for task_id in ALL_TASK_IDS
    ]

    results = await BenchmarkSuiteRunner().run_tasks(
        tasks,
        mode="repair",
        confirm_apply=True,
        use_llm_planner=True,
    )
    summary = summarize_results(results, mode="repair")

    assert summary.total_tasks == 10
    assert summary.patch_plan_count == 8
    assert summary.patch_review_count == 8
    assert summary.patch_review_blocked_count == 0
    assert summary.patch_applied_count == 8
    assert summary.verification_success_count == 8
    assert summary.scored_task_count == 8
    assert summary.env_repair_plan_count == 2
    assert summary.average_score == 1.0
