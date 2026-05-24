import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.agent.demo_orchestrator import DemoOrchestrator
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
    """Keep timestamps compact and readable in terminal output."""
    return event.timestamp.strftime("%H:%M:%S")


def print_event(event: Event) -> None:
    """Render one event as a beginner-friendly terminal line."""
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
    """Print events until the task sends its final TaskFinished event."""
    while True:
        event = await event_bus.next_event()
        print_event(event)

        if isinstance(event, TaskFinished):
            break


async def main() -> None:
    event_bus = EventBus()
    orchestrator = DemoOrchestrator(event_bus)

    orchestrator_task = asyncio.create_task(orchestrator.run())
    consumer_task = asyncio.create_task(consume_events(event_bus))

    await asyncio.gather(orchestrator_task, consumer_task)


if __name__ == "__main__":
    asyncio.run(main())
