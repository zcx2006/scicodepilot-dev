import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.backend.event_serializer import event_to_dict, event_to_json
from scicodepilot.events.schema import (
    CommandOutput,
    EnvRepairPlanCreated,
    PatchProposed,
    PatchReviewCreated,
    TaskStarted,
)


def test_event_to_dict_serializes_task_started() -> None:
    event = TaskStarted(task_id="task_1", task_name="Demo task")

    data = event_to_dict(event)

    assert data["type"] == "TaskStarted"
    assert data["task_id"] == "task_1"
    assert isinstance(data["timestamp"], str)


def test_event_to_json_returns_parseable_json() -> None:
    event = TaskStarted(task_id="task_1", task_name="Demo task")

    payload = event_to_json(event)
    data = json.loads(payload)

    assert isinstance(payload, str)
    assert data["type"] == "TaskStarted"
    assert data["task_id"] == "task_1"


def test_event_to_dict_serializes_command_output() -> None:
    event = CommandOutput(task_id="task_1", stream="stderr", content="boom")

    data = event_to_dict(event)

    assert data["type"] == "CommandOutput"
    assert data["stream"] == "stderr"
    assert data["content"] == "boom"


def test_event_to_dict_serializes_patch_proposed() -> None:
    event = PatchProposed(
        task_id="task_1",
        target_file="train.py",
        suspected_line=14,
        confidence=0.85,
        proposed_change="Change 128 to 64.",
        unified_diff="--- train.py\n+++ train.py",
    )

    data = event_to_dict(event)

    assert data["type"] == "PatchProposed"
    assert data["target_file"] == "train.py"
    assert data["confidence"] == 0.85


def test_event_to_dict_serializes_env_repair_plan_created() -> None:
    event = EnvRepairPlanCreated(
        task_id="repair_missing_module_003",
        error_type="missing_module",
        issue_category="dependency",
        summary="Missing Python module: demo_pkg.",
        suggested_actions=["Install the dependency inside the active conda environment."],
        requires_user_action=True,
        confidence=0.9,
    )

    data = event_to_dict(event)

    assert data["type"] == "EnvRepairPlanCreated"
    assert isinstance(data["timestamp"], str)
    assert data["suggested_actions"] == [
        "Install the dependency inside the active conda environment."
    ]
    assert data["requires_user_action"] is True


def test_event_to_dict_serializes_patch_review_created() -> None:
    event = PatchReviewCreated(
        task_id="repair_tensor_shape_001",
        approved=True,
        blocked=False,
        risk_level="low",
        reasons=["No blocking safety risks detected."],
        warnings=[],
    )

    data = event_to_dict(event)

    assert data["type"] == "PatchReviewCreated"
    assert isinstance(data["timestamp"], str)
    assert data["approved"] is True
    assert data["blocked"] is False
    assert data["risk_level"] == "low"
    assert data["reasons"] == ["No blocking safety risks detected."]
    assert data["warnings"] == []
