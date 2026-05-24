import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict
from scicodepilot.eval.suite_runner import BenchmarkSuiteRunner, summarize_results
from scicodepilot.eval.task_loader import load_benchmark_task


KEY_EVENT_TYPES = {
    "TaskStarted",
    "ErrorDetected",
    "FailureMemoryCreated",
    "EnvRepairPlanCreated",
    "PatchProposed",
    "PatchReviewCreated",
    "PatchApprovalRequired",
    "PatchApplied",
    "VerificationFinished",
    "TaskFinished",
}

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


def section(title: str) -> None:
    print()
    print(f"=== {title} ===")


def compact_event_summary(event: dict[str, Any]) -> str:
    event_type = event.get("type", "UnknownEvent")
    if event_type == "TaskStarted":
        return f"TaskStarted: {event.get('task_id')} - {event.get('task_name')}"
    if event_type == "ErrorDetected":
        return f"ErrorDetected: {event.get('error_type')} - {event.get('summary')}"
    if event_type == "FailureMemoryCreated":
        return (
            "FailureMemoryCreated: "
            f"{event.get('error_type')} | action={event.get('repair_action')}"
        )
    if event_type == "EnvRepairPlanCreated":
        actions = event.get("suggested_actions", [])
        first_action = actions[0] if actions else "manual action required"
        return (
            "EnvRepairPlanCreated: "
            f"category={event.get('issue_category')} | {first_action}"
        )
    if event_type == "PatchProposed":
        return (
            "PatchProposed: "
            f"target={event.get('target_file')} confidence={event.get('confidence')}"
        )
    if event_type == "PatchReviewCreated":
        return (
            "PatchReviewCreated: "
            f"approved={event.get('approved')} blocked={event.get('blocked')} "
            f"risk={event.get('risk_level')}"
        )
    if event_type == "PatchApprovalRequired":
        return f"PatchApprovalRequired: {event.get('message')}"
    if event_type == "PatchApplied":
        return (
            "PatchApplied: "
            f"success={event.get('success')} target={event.get('target_file')}"
        )
    if event_type == "VerificationFinished":
        return (
            "VerificationFinished: "
            f"success={event.get('success')} return_code={event.get('return_code')}"
        )
    if event_type == "TaskFinished":
        return f"TaskFinished: {event.get('status')} - {event.get('summary')}"
    return f"{event_type}: {event}"


async def print_task_event_story(
    controller: BackendController,
    task_id: str,
    mode: str,
    confirm_apply: bool = False,
) -> list[dict[str, Any]]:
    print(f"Running {task_id} mode={mode} confirm_apply={confirm_apply}")
    events: list[dict[str, Any]] = []
    async for event in controller.run_task(
        task_id=task_id,
        mode=mode,
        confirm_apply=confirm_apply,
    ):
        event_dict = event_to_dict(event)
        events.append(event_dict)
        if event_dict.get("type") in KEY_EVENT_TYPES:
            print(f"- {compact_event_summary(event_dict)}")
    return events


def print_task_list(controller: BackendController) -> None:
    section("Benchmark Tasks")
    tasks = controller.list_tasks()
    for index, task in enumerate(tasks, start=1):
        print(
            f"{index}. {task.task_id} | category={task.category} | "
            f"difficulty={task.difficulty}"
        )


def print_baseline_expectation() -> None:
    section("M19 Baseline Suite Expectation")
    print("- total_tasks = 10")
    print("- patch_plan_count = 8")
    print("- patch_review_count = 8")
    print("- patch_review_blocked_count = 0")
    print("- env_repair_plan_count = 2")
    print("- average_score = 1.0")


def print_integrity_hints() -> None:
    section("Original Benchmark Integrity Checks")
    print("Run these to confirm original bugs remain untouched:")
    print("grep \"classifier_expected_dim\" benchmark/tasks/repair_tensor_shape_001/repo/train.py")
    print("grep \"float64\" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py")
    print("grep \"mainn\" benchmark/tasks/repair_entrypoint_error_005/repo/train.py")
    print("grep \"batch_size + 1\" benchmark/tasks/repair_label_shape_006/repo/train.py")


def print_docs_hints() -> None:
    section("Documentation Pack")
    print("- docs/architecture.md")
    print("- docs/demo_guide.md")
    print("- docs/final_status.md")
    print("- docs/frontend_handoff_checklist.md")


def load_all_tasks():
    return [
        load_benchmark_task(PROJECT_ROOT / "benchmark" / "tasks" / task_id)
        for task_id in ALL_TASK_IDS
    ]


def print_summary(prefix: str, summary) -> None:
    print(prefix)
    print(f"- total_tasks: {summary.total_tasks}")
    print(f"- diagnosis_pass_count: {summary.diagnosis_pass_count}")
    print(f"- patch_plan_count: {summary.patch_plan_count}")
    print(f"- patch_review_count: {summary.patch_review_count}")
    print(f"- patch_review_blocked_count: {summary.patch_review_blocked_count}")
    print(f"- patch_applied_count: {summary.patch_applied_count}")
    print(f"- verification_success_count: {summary.verification_success_count}")
    print(f"- scored_task_count: {summary.scored_task_count}")
    print(f"- env_repair_plan_count: {summary.env_repair_plan_count}")
    print(f"- average_score: {summary.average_score}")


async def run_full_suite_showcase() -> None:
    section("Full Suite Summary")
    tasks = load_all_tasks()
    diagnosis_results = await BenchmarkSuiteRunner().run_tasks(tasks, mode="diagnosis")
    diagnosis_summary = summarize_results(diagnosis_results, mode="diagnosis")
    print_summary("Diagnosis suite:", diagnosis_summary)

    repair_results = await BenchmarkSuiteRunner().run_tasks(
        tasks,
        mode="repair",
        confirm_apply=True,
    )
    repair_summary = summarize_results(repair_results, mode="repair")
    print_summary("Repair suite with confirmation:", repair_summary)


async def run_mock_llm_showcase() -> None:
    section("Mock LLM Planner Suite")
    os.environ["SCICODEPILOT_LLM_PROVIDER"] = "mock"
    tasks = load_all_tasks()
    results = await BenchmarkSuiteRunner().run_tasks(
        tasks,
        mode="repair",
        confirm_apply=True,
        use_llm_planner=True,
    )
    summary = summarize_results(results, mode="repair")
    print_summary("Mock LLM repair suite:", summary)


async def smoke_test() -> None:
    controller = BackendController()
    tasks = controller.list_tasks()
    print("SciCodePilot M20 Showcase smoke test")
    print(f"tasks: {len(tasks)}")
    print("BackendController import/list_tasks OK")


async def main() -> None:
    parser = argparse.ArgumentParser(description="SciCodePilot M20 showcase runner")
    parser.add_argument("--full", action="store_true", help="Run full suite summaries.")
    parser.add_argument(
        "--use-mock-llm",
        action="store_true",
        help="Run an additional mock LLM planner repair suite.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Check imports and task discovery without running benchmarks.",
    )
    args = parser.parse_args()

    if args.smoke_test:
        await smoke_test()
        return

    section("SciCodePilot M20 Showcase")
    print("Environment: WSL Ubuntu + conda env scicodepilot-dev")
    print("Public API: BackendController + event_to_dict/event_to_json")
    print("LLM planner: optional and disabled by default")

    controller = BackendController()
    print_task_list(controller)

    section("Diagnosis Story")
    await print_task_event_story(
        controller,
        task_id="repair_tensor_shape_001",
        mode="diagnosis",
    )

    section("Repair Proposal Without Confirmation")
    await print_task_event_story(
        controller,
        task_id="repair_tensor_shape_001",
        mode="repair",
        confirm_apply=False,
    )
    print("Safety note: no patch is applied without explicit confirmation.")

    section("Repair With Confirmation")
    await print_task_event_story(
        controller,
        task_id="repair_tensor_shape_001",
        mode="repair",
        confirm_apply=True,
    )
    print("Score note: score.json is produced by the hidden evaluator in the isolated workspace.")

    section("EnvDoctor Story")
    await print_task_event_story(
        controller,
        task_id="repair_missing_module_003",
        mode="repair",
        confirm_apply=False,
    )
    print("EnvDoctor note: dependency/data issues generate plans only; no pip install or file creation.")

    print_baseline_expectation()

    if args.full:
        await run_full_suite_showcase()

    if args.use_mock_llm:
        await run_mock_llm_showcase()

    print_integrity_hints()
    print_docs_hints()


if __name__ == "__main__":
    asyncio.run(main())
