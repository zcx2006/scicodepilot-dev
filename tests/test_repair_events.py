import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.events.schema import (
    EnvRepairPlanCreated,
    PatchApprovalRequired,
    PatchApplied,
    PatchProposed,
    VerificationFinished,
    VerificationStarted,
)


def test_patch_applied_event_model() -> None:
    event = PatchApplied(
        task_id="repair_tensor_shape_001",
        target_file="train.py",
        success=True,
        message="Patch plan was applied successfully.",
        unified_diff="--- train.py\n+++ train.py",
    )

    assert event.type == "PatchApplied"
    assert event.success is True
    assert event.target_file == "train.py"


def test_patch_proposed_event_model() -> None:
    event = PatchProposed(
        task_id="repair_tensor_shape_001",
        target_file="train.py",
        suspected_line=14,
        confidence=0.85,
        proposed_change="Change classifier_expected_dim from 128 to 64.",
        unified_diff="--- train.py\n+++ train.py",
    )

    assert event.type == "PatchProposed"
    assert event.target_file == "train.py"
    assert event.confidence == 0.85


def test_patch_approval_required_event_model() -> None:
    event = PatchApprovalRequired(
        task_id="repair_tensor_shape_001",
        target_file="train.py",
        message="Patch application requires explicit confirmation.",
        unified_diff="--- train.py\n+++ train.py",
    )

    assert event.type == "PatchApprovalRequired"
    assert event.target_file == "train.py"


def test_verification_started_event_model() -> None:
    event = VerificationStarted(
        task_id="repair_tensor_shape_001",
        command="python train.py",
        cwd="/tmp/repo",
    )

    assert event.type == "VerificationStarted"
    assert event.command == "python train.py"


def test_verification_finished_event_model() -> None:
    event = VerificationFinished(
        task_id="repair_tensor_shape_001",
        command="python train.py",
        return_code=0,
        success=True,
        summary="Verification command succeeded.",
    )

    assert event.type == "VerificationFinished"
    assert event.success is True
    assert event.return_code == 0


def test_env_repair_plan_created_event_model() -> None:
    event = EnvRepairPlanCreated(
        task_id="repair_missing_file_004",
        error_type="missing_file",
        issue_category="data",
        summary="Missing required file: data/train.csv.",
        suggested_actions=["Download or place the required dataset/config file."],
        requires_user_action=True,
        confidence=0.9,
    )

    assert event.type == "EnvRepairPlanCreated"
    assert event.issue_category == "data"
    assert event.requires_user_action is True
