import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.backend.controller import BackendController


def collect_event_types(events) -> list[str]:
    return [event.type for event in events]


def test_backend_controller_list_tasks() -> None:
    controller = BackendController()

    tasks = controller.list_tasks()
    task_ids = [task.task_id for task in tasks]

    assert "repair_tensor_shape_001" in task_ids
    assert "repair_dtype_mismatch_002" in task_ids
    assert "repair_missing_module_003" in task_ids
    assert task_ids == sorted(task_ids)


def test_backend_controller_get_task() -> None:
    task = BackendController().get_task("repair_tensor_shape_001")

    assert task.task_id == "repair_tensor_shape_001"


def test_backend_controller_get_unknown_task_raises() -> None:
    with pytest.raises(ValueError):
        BackendController().get_task("unknown_task")


@pytest.mark.asyncio
async def test_backend_controller_run_task_diagnosis_yields_events() -> None:
    controller = BackendController()
    events = []

    async for event in controller.run_task(
        task_id="repair_missing_module_003",
        mode="diagnosis",
    ):
        events.append(event)

    event_types = collect_event_types(events)
    assert "TaskStarted" in event_types
    assert "ErrorDetected" in event_types
    assert "FailureMemoryCreated" in event_types
    assert event_types[-1] == "TaskFinished"


@pytest.mark.asyncio
async def test_backend_controller_run_task_repair_missing_module_yields_events() -> None:
    controller = BackendController()
    events = []

    async for event in controller.run_task(
        task_id="repair_missing_module_003",
        mode="repair",
        confirm_apply=False,
    ):
        events.append(event)

    event_types = collect_event_types(events)
    assert "TaskStarted" in event_types
    assert "ErrorDetected" in event_types
    assert event_types[-1] == "TaskFinished"


@pytest.mark.asyncio
async def test_backend_controller_run_task_repair_default_requires_confirmation_when_plan_exists() -> None:
    pytest.importorskip("torch")
    controller = BackendController()
    events = []

    async for event in controller.run_task(
        task_id="repair_tensor_shape_001",
        mode="repair",
        confirm_apply=False,
    ):
        events.append(event)

    event_types = collect_event_types(events)
    assert "PatchProposed" in event_types
    assert "PatchApprovalRequired" in event_types
    assert "PatchApplied" not in event_types
    assert event_types[-1] == "TaskFinished"


@pytest.mark.asyncio
async def test_backend_controller_invalid_mode_raises() -> None:
    controller = BackendController()

    with pytest.raises(ValueError):
        async for _event in controller.run_task(
            task_id="repair_missing_module_003",
            mode="bad_mode",
        ):
            pass
