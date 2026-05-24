import asyncio

from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import (
    ErrorDetected,
    FailureMemoryCreated,
    PlanCreated,
    StepStarted,
    TaskFinished,
    TaskStarted,
)
from scicodepilot.memory.failure_memory import FailureMemoryBuilder
from scicodepilot.tools.shell_tool import ShellTool
from scicodepilot.tools.traceback_parser import ParsedError, TracebackParser


class DemoOrchestrator:
    """A fake backend orchestrator that only emits demo events."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def run(self) -> None:
        """Simulate one task flow without calling an LLM or running commands."""
        task_id = "demo_task_001"
        task_name = "Repair tensor shape mismatch demo"
        steps = [
            "Inspect the target training script",
            "Run the baseline command",
            "Analyze the runtime error",
            "Create structured failure memory",
        ]

        await self.event_bus.emit(TaskStarted(task_id=task_id, task_name=task_name))
        await asyncio.sleep(0.15)

        await self.event_bus.emit(PlanCreated(task_id=task_id, steps=steps))
        await asyncio.sleep(0.15)

        await self.event_bus.emit(
            StepStarted(
                task_id=task_id,
                step_index=1,
                step_name="Run the baseline command",
            )
        )
        await asyncio.sleep(0.15)

        shell_tool = ShellTool(self.event_bus)
        parser = TracebackParser()
        memory_builder = FailureMemoryBuilder()

        command_result = await shell_tool.run(
            task_id=task_id,
            command="python scripts/mock_training_error.py",
        )

        if not command_result.success:
            parsed_error = parser.parse(command_result.stderr_lines)
            if parsed_error is None:
                parsed_error = ParsedError(
                    error_type="unknown_error",
                    summary=(
                        "The command failed, but no known error pattern was "
                        "matched by the current parser."
                    ),
                    evidence=command_result.stderr_lines,
                )

            await asyncio.sleep(0.15)
            await self.event_bus.emit(
                ErrorDetected(
                    task_id=task_id,
                    error_type=parsed_error.error_type,
                    summary=parsed_error.summary,
                    evidence=parsed_error.evidence,
                )
            )
            await asyncio.sleep(0.15)

            failure_memory = memory_builder.from_parsed_error(parsed_error)
            await self.event_bus.emit(
                FailureMemoryCreated(
                    task_id=task_id,
                    error_type=failure_memory.error_type,
                    evidence=failure_memory.evidence,
                    root_cause_hypothesis=failure_memory.root_cause_hypothesis,
                    repair_action=failure_memory.repair_action,
                )
            )
            await asyncio.sleep(0.15)

        await self.event_bus.emit(
            TaskFinished(
                task_id=task_id,
                status="demo_finished",
                summary=(
                    "Demo event flow completed with rule-based error parsing "
                    "and structured failure memory generation."
                ),
            )
        )
