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


def test_patch_applier_insertion_changes_only_workspace(tmp_path) -> None:
    original_repo = tmp_path / "original"
    workspace_repo = tmp_path / "workspace"
    original_repo.mkdir()
    workspace_repo.mkdir()
    original_text = (
        "def cli_bool_option(params, command_option, param):\n"
        "    param = params.get(param)\n"
        "    assert isinstance(param, bool)\n"
        "    return [command_option] if param else []\n"
    )
    (original_repo / "sample.py").write_text(original_text, encoding="utf-8")
    (workspace_repo / "sample.py").write_text(original_text, encoding="utf-8")
    patch_plan = make_patch_plan(
        "--- sample.py\n"
        "+++ sample.py\n"
        "@@ -1,4 +1,6 @@\n"
        " def cli_bool_option(params, command_option, param):\n"
        "     param = params.get(param)\n"
        "+    if param is None:\n"
        "+        return []\n"
        "     assert isinstance(param, bool)\n"
        "     return [command_option] if param else []",
        target_file="sample.py",
    )

    applied = PatchApplier().apply(str(workspace_repo), patch_plan)

    assert applied is True
    assert (original_repo / "sample.py").read_text(encoding="utf-8") == original_text
    workspace_text = (workspace_repo / "sample.py").read_text(encoding="utf-8")
    assert "if param is None:" in workspace_text
