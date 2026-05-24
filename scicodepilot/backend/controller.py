import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from pydantic import BaseModel

from scicodepilot.eval.diagnosis_runner import DiagnosisBenchmarkRunner
from scicodepilot.eval.task_loader import BenchmarkTask, load_benchmark_task
from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import Event, TaskFinished
from scicodepilot.repair.repair_policy import RepairPolicy
from scicodepilot.repair.repair_runner import RepairBenchmarkRunner


class TaskInfo(BaseModel):
    """Small task card for frontend task selection."""

    task_id: str
    task_name: str
    category: str
    difficulty: str
    requires: list[str]


class BackendController:
    """Stable backend entrypoint for frontend clients."""

    def __init__(self, benchmark_root: str | Path = "benchmark/tasks") -> None:
        self.benchmark_root = Path(benchmark_root)

    def list_tasks(self) -> list[TaskInfo]:
        """Return all known benchmark tasks sorted by task_id."""
        tasks = [
            load_benchmark_task(metadata_path.parent)
            for metadata_path in self.benchmark_root.glob("*/metadata.json")
        ]
        return [
            TaskInfo(
                task_id=task.task_id,
                task_name=task.task_name,
                category=task.category,
                difficulty=task.difficulty,
                requires=task.requires,
            )
            for task in sorted(tasks, key=lambda item: item.task_id)
        ]

    def get_task(self, task_id: str) -> BenchmarkTask:
        """Load one benchmark task by id, or raise ValueError."""
        task_dir = self.benchmark_root / task_id
        metadata_path = task_dir / "metadata.json"
        if not metadata_path.exists():
            raise ValueError(f"Unknown task_id: {task_id}")

        return load_benchmark_task(task_dir)

    async def run_task(
        self,
        task_id: str,
        mode: str,
        confirm_apply: bool = False,
    ) -> AsyncIterator[Event]:
        """Run one task and yield backend events until TaskFinished."""
        task = self.get_task(task_id)
        event_bus = EventBus()

        if mode == "diagnosis":
            runner = DiagnosisBenchmarkRunner(event_bus)
            runner_task = asyncio.create_task(runner.run(task))
        elif mode == "repair":
            runner = RepairBenchmarkRunner(event_bus)
            policy = RepairPolicy(
                require_confirmation=True,
                approved=confirm_apply,
            )
            runner_task = asyncio.create_task(runner.run(task, policy=policy))
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        while True:
            event = await event_bus.next_event()
            yield event

            if isinstance(event, TaskFinished):
                await runner_task
                break
