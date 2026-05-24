import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.repair.patch_applier import PatchApplier
from scicodepilot.repair.patch_plan import PatchPlan


def make_patch_plan(unified_diff: str, target_file: str = "train.py") -> PatchPlan:
    return PatchPlan(
        task_id="repair_tensor_shape_001",
        error_type="tensor_shape",
        target_file=target_file,
        suspected_line=2,
        rationale="Test rationale.",
        proposed_change="Change classifier_expected_dim from 128 to 64.",
        unified_diff=unified_diff,
        confidence=0.85,
    )


def test_patch_applier_applies_simple_diff_to_temp_file(tmp_path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    train_path = repo_dir / "train.py"
    train_path.write_text(
        "def main():\n"
        "    classifier_expected_dim = 128\n"
        "    num_classes = 10\n",
        encoding="utf-8",
    )
    patch_plan = make_patch_plan(
        "--- train.py\n"
        "+++ train.py\n"
        "@@ -1,3 +1,3 @@\n"
        " def main():\n"
        "-    classifier_expected_dim = 128\n"
        "+    classifier_expected_dim = 64\n"
        "     num_classes = 10"
    )

    applied = PatchApplier().apply(str(repo_dir), patch_plan)

    content = train_path.read_text(encoding="utf-8")
    assert applied is True
    assert "classifier_expected_dim = 64" in content
    assert "classifier_expected_dim = 128" not in content


def test_patch_applier_returns_false_when_old_line_missing(tmp_path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    train_path = repo_dir / "train.py"
    original_content = "def main():\n    num_classes = 10\n"
    train_path.write_text(original_content, encoding="utf-8")
    patch_plan = make_patch_plan(
        "--- train.py\n"
        "+++ train.py\n"
        "@@\n"
        "-    classifier_expected_dim = 128\n"
        "+    classifier_expected_dim = 64"
    )

    applied = PatchApplier().apply(str(repo_dir), patch_plan)

    assert applied is False
    assert train_path.read_text(encoding="utf-8") == original_content


def test_patch_applier_returns_false_for_missing_target_file(tmp_path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    patch_plan = make_patch_plan(
        "--- train.py\n"
        "+++ train.py\n"
        "@@\n"
        "-    classifier_expected_dim = 128\n"
        "+    classifier_expected_dim = 64"
    )

    applied = PatchApplier().apply(str(repo_dir), patch_plan)

    assert applied is False


def test_patch_applier_does_not_modify_file_when_apply_fails(tmp_path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    train_path = repo_dir / "train.py"
    original_content = "def main():\n    classifier_expected_dim = 256\n"
    train_path.write_text(original_content, encoding="utf-8")
    patch_plan = make_patch_plan(
        "--- train.py\n"
        "+++ train.py\n"
        "@@\n"
        "-    classifier_expected_dim = 128\n"
        "+    classifier_expected_dim = 64"
    )

    applied = PatchApplier().apply(str(repo_dir), patch_plan)

    assert applied is False
    assert train_path.read_text(encoding="utf-8") == original_content
