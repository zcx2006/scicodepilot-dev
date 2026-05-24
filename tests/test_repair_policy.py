import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.repair.repair_policy import RepairPolicy


def test_default_policy_requires_confirmation() -> None:
    policy = RepairPolicy()

    assert policy.require_confirmation is True
    assert policy.approved is False
    assert policy.can_apply_patch() is False


def test_policy_can_apply_when_approved() -> None:
    policy = RepairPolicy(require_confirmation=True, approved=True)

    assert policy.can_apply_patch() is True


def test_policy_can_apply_when_confirmation_disabled() -> None:
    policy = RepairPolicy(require_confirmation=False, approved=False)

    assert policy.can_apply_patch() is True
