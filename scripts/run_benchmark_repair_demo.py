import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.task_loader import load_benchmark_task
from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import (
    CommandFinished,
    CommandOutput,
    CommandStarted,
    ErrorDetected,
    Event,
    FailureMemoryCreated,
    PatchApprovalRequired,
    PatchApplied,
    PatchProposed,
    PlanCreated,
    StepStarted,
    TaskFinished,
    TaskStarted,
    VerificationFinished,
    VerificationStarted,
)
from scicodepilot.repair.repair_policy import RepairPolicy
from scicodepilot.repair.repair_runner import RepairBenchmarkRunner
from scicodepilot.repair.repair_result import RepairResult


def format_time(event: Event) -> str:
    return event.timestamp.strftime("%H:%M:%S")


def print_event(event: Event) -> None:
    time_text = format_time(event)

    if isinstance(event, TaskStarted):
        print(f"{time_text} [TaskStarted] {event.task_id} - {event.task_name}")
    elif isinstance(event, PlanCreated):
        print(f"{time_text} [PlanCreated] {len(event.steps)} steps created")
    elif isinstance(event, StepStarted):
        print(
            f"{time_text} [StepStarted] "
            f"Step {event.step_index}: {event.step_name}"
        )
    elif isinstance(event, CommandStarted):
        print(f"{time_text} [CommandStarted] {event.command}")
    elif isinstance(event, CommandOutput):
        print(f"{time_text} [{event.stream}] {event.content}")
    elif isinstance(event, CommandFinished):
        print(
            f"{time_text} [CommandFinished] "
            f"return_code={event.return_code} success={event.success}"
        )
    elif isinstance(event, ErrorDetected):
        print(f"{time_text} [ErrorDetected] {event.error_type} - {event.summary}")
    elif isinstance(event, FailureMemoryCreated):
        print(f"{time_text} [FailureMemoryCreated] {event.error_type}")
    elif isinstance(event, PatchProposed):
        print(
            f"{time_text} [PatchProposed] "
            f"target_file={event.target_file} confidence={event.confidence}"
        )
    elif isinstance(event, PatchApprovalRequired):
        print(
            f"{time_text} [PatchApprovalRequired] "
            f"target_file={event.target_file} - {event.message}"
        )
    elif isinstance(event, PatchApplied):
        print(
            f"{time_text} [PatchApplied] "
            f"success={event.success} target_file={event.target_file}"
        )
    elif isinstance(event, VerificationStarted):
        print(f"{time_text} [VerificationStarted] {event.command}")
    elif isinstance(event, VerificationFinished):
        print(
            f"{time_text} [VerificationFinished] "
            f"success={event.success} return_code={event.return_code}"
        )
    elif isinstance(event, TaskFinished):
        print(f"{time_text} [TaskFinished] {event.status} - {event.summary}")


async def consume_events(event_bus: EventBus) -> None:
    while True:
        event = await event_bus.next_event()
        print_event(event)

        if isinstance(event, TaskFinished):
            break


def print_repair_summary(result: RepairResult) -> None:
    print()
    print("=== Repair Summary ===")
    print(f"task_id: {result.task_id}")
    print(f"patch_applied: {result.patch_applied}")
    print(f"target_file: {result.target_file}")
    print(f"verification_command: {result.verification_command}")
    print(f"verification_success: {result.verification_success}")
    print(f"verification_return_code: {result.verification_return_code}")
    print(f"patch_plan_generated: {result.patch_plan_generated}")
    print(f"requires_confirmation: {result.requires_confirmation}")
    print(f"confirmation_granted: {result.confirmation_granted}")
    print(f"message: {result.message}")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--confirm-apply",
        action="store_true",
        help="Explicitly approve applying the generated patch plan.",
    )
    parser.add_argument("--use-llm-planner", action="store_true")
    args = parser.parse_args()

    task_dir = PROJECT_ROOT / "benchmark" / "tasks" / "repair_tensor_shape_001"
    task = load_benchmark_task(task_dir)
    event_bus = EventBus()
    runner = RepairBenchmarkRunner(event_bus)
    policy = RepairPolicy(
        require_confirmation=True,
        approved=args.confirm_apply,
    )

    if args.use_llm_planner:
        print("LLM patch planner enabled; using configured client or deterministic mock mode.")

    runner_task = asyncio.create_task(
        runner.run(
            task,
            policy=policy,
            use_llm_planner=args.use_llm_planner,
        )
    )
    consumer_task = asyncio.create_task(consume_events(event_bus))

    repair_result = await runner_task
    await consumer_task
    print_repair_summary(repair_result)


if __name__ == "__main__":
    asyncio.run(main())
