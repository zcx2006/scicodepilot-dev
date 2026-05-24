import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.repair.patch_plan import PatchPlan
from scicodepilot.review.patch_safety_reviewer import PatchSafetyReviewer


def make_patch_plan(
    target_file: str = "train.py",
    unified_diff: str | None = None,
    error_type: str = "tensor_shape",
    proposed_change: str = "Change classifier_expected_dim from 128 to 64.",
) -> PatchPlan:
    return PatchPlan(
        task_id="task_1",
        error_type=error_type,
        target_file=target_file,
        suspected_line=4,
        rationale="Test rationale.",
        proposed_change=proposed_change,
        unified_diff=unified_diff
        if unified_diff is not None
        else (
            "--- train.py\n"
            "+++ train.py\n"
            "@@\n"
            "-    classifier_expected_dim = 128\n"
            "+    classifier_expected_dim = 64\n"
        ),
        confidence=0.8,
    )


def review(plan: PatchPlan, tmp_path: Path):
    return PatchSafetyReviewer().review(plan, str(tmp_path))


def test_legal_tensor_shape_patch_is_approved(tmp_path) -> None:
    result = review(make_patch_plan(), tmp_path)

    assert result.approved is True
    assert result.blocked is False
    assert result.risk_level in {"low", "medium"}


def test_empty_diff_is_blocked(tmp_path) -> None:
    result = review(make_patch_plan(unified_diff=""), tmp_path)

    assert result.approved is False
    assert result.blocked is True
    assert result.risk_level == "high"


def test_absolute_target_file_is_blocked(tmp_path) -> None:
    result = review(make_patch_plan(target_file="/tmp/train.py"), tmp_path)

    assert result.blocked is True


def test_path_traversal_is_blocked(tmp_path) -> None:
    result = review(make_patch_plan(target_file="../train.py"), tmp_path)

    assert result.blocked is True


def test_blocked_target_areas_are_blocked(tmp_path) -> None:
    for target_file in [
        "benchmark/train.py",
        "outputs/train.py",
        "reference/train.py",
        "tests/test_train.py",
        ".git/config",
        "requirements.txt",
        "pyproject.toml",
    ]:
        result = review(make_patch_plan(target_file=target_file), tmp_path)
        assert result.blocked is True


def test_rm_rf_in_diff_is_blocked(tmp_path) -> None:
    result = review(
        make_patch_plan(
            proposed_change="Change an unrelated value.",
            unified_diff=(
                "--- train.py\n"
                "+++ train.py\n"
                "@@\n"
                "-    pass\n"
                "+    os.system('rm -rf /tmp/demo')\n"
            )
        ),
        tmp_path,
    )

    assert result.blocked is True


def test_pip_install_in_diff_is_blocked(tmp_path) -> None:
    result = review(
        make_patch_plan(
            proposed_change="Change an unrelated value.",
            unified_diff=(
                "--- train.py\n"
                "+++ train.py\n"
                "@@\n"
                "-    pass\n"
                "+    # pip install missing-package\n"
            )
        ),
        tmp_path,
    )

    assert result.blocked is True


def test_other_dangerous_terms_in_diff_are_blocked(tmp_path) -> None:
    for term in [
        "conda install torch",
        "sudo apt install",
        "subprocess.run(['echo'])",
        "eval('1 + 1')",
        "exec('x = 1')",
    ]:
        result = review(
            make_patch_plan(
                proposed_change="Change an unrelated value.",
                unified_diff=(
                    "--- train.py\n"
                    "+++ train.py\n"
                    "@@\n"
                    "-    pass\n"
                    f"+    {term}\n"
                ),
            ),
            tmp_path,
        )
        assert result.blocked is True


def test_weak_alignment_warns_and_raises_risk_without_blocking(tmp_path) -> None:
    result = review(
        make_patch_plan(
            proposed_change="Change an unrelated value.",
            unified_diff=(
                "--- train.py\n"
                "+++ train.py\n"
                "@@\n"
                "-    value = 1\n"
                "+    value = 2\n"
            )
        ),
        tmp_path,
    )

    assert result.blocked is False
    assert result.approved is True
    assert result.risk_level == "medium"
    assert result.warnings


def test_multi_file_diff_is_blocked(tmp_path) -> None:
    result = review(
        make_patch_plan(
            unified_diff=(
                "--- train.py\n"
                "+++ train.py\n"
                "@@\n"
                "-    classifier_expected_dim = 128\n"
                "+    classifier_expected_dim = 64\n"
                "--- other.py\n"
                "+++ other.py\n"
                "@@\n"
                "-x\n"
                "+y\n"
            )
        ),
        tmp_path,
    )

    assert result.blocked is True
