import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.diagnosis_runner import DiagnosisBenchmarkRunner
from scicodepilot.eval.task_loader import load_benchmark_task
from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import (
    CommandFinished,
    CommandOutput,
    CommandStarted,
    ErrorDetected,
    Event,
    FailureMemoryCreated,
    PlanCreated,
    StepStarted,
    TaskFinished,
    TaskStarted,
)


def format_time(event: Event) -> str:
    return event.timestamp.strftime("%H:%M:%S")


def print_event(event: Event) -> None:
    time_text = format_time(event)

    if isinstance(event, TaskStarted):
        print(f"{time_text} [TaskStarted] {event.task_id} - {event.task_name}")
    elif isinstance(event, PlanCreated):
        print(f"{time_text} [PlanCreated] {len(event.steps)} steps created")
        for index, step in enumerate(event.steps, start=1):
            print(f"  {index}. {step}")
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
        for item in event.evidence:
            print(f"  evidence: {item}")
    elif isinstance(event, FailureMemoryCreated):
        print(f"{time_text} [FailureMemoryCreated] {event.error_type}")
        print(f"  root cause: {event.root_cause_hypothesis}")
        print(f"  repair: {event.repair_action}")
    elif isinstance(event, TaskFinished):
        print(f"{time_text} [TaskFinished] {event.status} - {event.summary}")


async def consume_events(event_bus: EventBus) -> None:
    while True:
        event = await event_bus.next_event()
        print_event(event)

        if isinstance(event, TaskFinished):
            break


def print_summary(result) -> None:
    parsed_error_type = result.parsed_error.error_type if result.parsed_error else None
    diagnosis_passed = result.evaluation.passed if result.evaluation else None

    print()
    print("=== Diagnosis Benchmark Summary ===")
    print(f"task_id: {result.task_id}")
    print(f"command_success: {result.command_success}")
    print(f"parsed_error: {parsed_error_type}")
    print(f"diagnosis_passed: {diagnosis_passed}")

    if result.evaluation is not None:
        print()
        print("checks:")
        for check_name, passed in result.evaluation.checks.items():
            print(f"- {check_name}: {passed}")

    print()
    print("=== Patch Plan ===")
    if result.patch_plan is None:
        print("No patch plan generated.")
        return

    print(f"target_file: {result.patch_plan.target_file}")
    print(f"suspected_line: {result.patch_plan.suspected_line}")
    print(f"confidence: {result.patch_plan.confidence}")
    print(f"rationale: {result.patch_plan.rationale}")
    print(f"proposed_change: {result.patch_plan.proposed_change}")
    print("unified_diff:")
    print(result.patch_plan.unified_diff)


async def main() -> None:
    task_dir = PROJECT_ROOT / "benchmark" / "tasks" / "repair_tensor_shape_001"
    task = load_benchmark_task(task_dir)
    event_bus = EventBus()
    runner = DiagnosisBenchmarkRunner(event_bus)

    runner_task = asyncio.create_task(runner.run(task))
    consumer_task = asyncio.create_task(consume_events(event_bus))

    result = await runner_task
    await consumer_task
    print_summary(result)


if __name__ == "__main__":
    asyncio.run(main())
