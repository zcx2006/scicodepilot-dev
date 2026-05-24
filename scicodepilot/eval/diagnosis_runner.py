import asyncio

from pydantic import BaseModel

from scicodepilot.eval.diagnosis_evaluator import (
    DiagnosisEvaluationResult,
    evaluate_diagnosis,
    load_expected_diagnosis,
)
from scicodepilot.eval.task_loader import BenchmarkTask
from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import (
    ErrorDetected,
    FailureMemoryCreated,
    PlanCreated,
    StepStarted,
    TaskFinished,
    TaskStarted,
)
from scicodepilot.memory.failure_memory import FailureMemory, FailureMemoryBuilder
from scicodepilot.repair.patch_plan import PatchPlan
from scicodepilot.repair.patch_planner import PatchPlanner
from scicodepilot.tools.shell_tool import ShellTool
from scicodepilot.tools.traceback_parser import ParsedError, TracebackParser


class DiagnosisRunResult(BaseModel):
    """Final result returned by one diagnosis benchmark run."""

    task_id: str
    command_success: bool
    parsed_error: ParsedError | None
    failure_memory: FailureMemory | None
    evaluation: DiagnosisEvaluationResult | None
    patch_plan: PatchPlan | None = None


class DiagnosisBenchmarkRunner:
    """Run a diagnosis-only benchmark task through the backend pipeline."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def run(self, task: BenchmarkTask) -> DiagnosisRunResult:
        shell_tool = ShellTool(self.event_bus)
        parser = TracebackParser()
        memory_builder = FailureMemoryBuilder()

        await self.event_bus.emit(
            TaskStarted(task_id=task.task_id, task_name=task.task_name)
        )
        await asyncio.sleep(0.15)

        await self.event_bus.emit(
            PlanCreated(
                task_id=task.task_id,
                steps=[
                    "Load benchmark task metadata",
                    "Run the task entry command",
                    "Parse the runtime failure",
                    "Generate structured failure memory",
                    "Evaluate diagnosis against expected benchmark criteria",
                ],
            )
        )
        await asyncio.sleep(0.15)

        await self.event_bus.emit(
            StepStarted(
                task_id=task.task_id,
                step_index=1,
                step_name="Run the task entry command",
            )
        )
        await asyncio.sleep(0.15)

        command_result = await shell_tool.run(
            task_id=task.task_id,
            command=task.entry_command,
            cwd=task.repo_dir,
        )

        if command_result.success:
            await self.event_bus.emit(
                TaskFinished(
                    task_id=task.task_id,
                    status="success",
                    summary="Benchmark task command succeeded; no diagnosis was required.",
                )
            )
            return DiagnosisRunResult(
                task_id=task.task_id,
                command_success=True,
                parsed_error=None,
                failure_memory=None,
                evaluation=None,
                patch_plan=None,
            )

        parsed_error = parser.parse(command_result.stderr_lines)
        if parsed_error is None:
            await self.event_bus.emit(
                ErrorDetected(
                    task_id=task.task_id,
                    error_type="unknown_error",
                    summary=(
                        "The command failed, but no known parser rule matched "
                        "the stderr output."
                    ),
                    evidence=command_result.stderr_lines,
                )
            )
            await self.event_bus.emit(
                TaskFinished(
                    task_id=task.task_id,
                    status="failed",
                    summary="Benchmark task failed, but no known diagnosis rule matched.",
                )
            )
            return DiagnosisRunResult(
                task_id=task.task_id,
                command_success=False,
                parsed_error=None,
                failure_memory=None,
                evaluation=None,
                patch_plan=None,
            )

        await self.event_bus.emit(
            ErrorDetected(
                task_id=task.task_id,
                error_type=parsed_error.error_type,
                summary=parsed_error.summary,
                evidence=parsed_error.evidence,
            )
        )
        await asyncio.sleep(0.15)

        failure_memory = memory_builder.from_parsed_error(parsed_error)
        await self.event_bus.emit(
            FailureMemoryCreated(
                task_id=task.task_id,
                error_type=failure_memory.error_type,
                evidence=failure_memory.evidence,
                root_cause_hypothesis=failure_memory.root_cause_hypothesis,
                repair_action=failure_memory.repair_action,
            )
        )
        await asyncio.sleep(0.15)

        expected = load_expected_diagnosis(task.expected_diagnosis_path)
        evaluation = evaluate_diagnosis(parsed_error, failure_memory, expected)
        patch_plan = PatchPlanner().create_plan(
            task_id=task.task_id,
            repo_dir=task.repo_dir,
            parsed_error=parsed_error,
            failure_memory=failure_memory,
        )
        summary = (
            "Benchmark diagnosis completed and matched the expected diagnosis criteria."
            if evaluation.passed
            else "Benchmark diagnosis completed but did not match the expected diagnosis criteria."
        )

        await self.event_bus.emit(
            TaskFinished(
                task_id=task.task_id,
                status="demo_finished" if evaluation.passed else "failed",
                summary=summary,
            )
        )

        return DiagnosisRunResult(
            task_id=task.task_id,
            command_success=False,
            parsed_error=parsed_error,
            failure_memory=failure_memory,
            evaluation=evaluation,
            patch_plan=patch_plan,
        )
