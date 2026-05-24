import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_showcase_script_exists() -> None:
    assert (PROJECT_ROOT / "scripts" / "run_showcase.py").exists()


def test_showcase_script_help_runs() -> None:
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "run_showcase.py"), "--help"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--smoke-test" in result.stdout


def test_showcase_script_smoke_test_runs_without_api_key() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_showcase.py"),
            "--smoke-test",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "BackendController import/list_tasks OK" in result.stdout


def test_m20_docs_exist_and_include_key_terms() -> None:
    docs = [
        PROJECT_ROOT / "docs" / "architecture.md",
        PROJECT_ROOT / "docs" / "demo_guide.md",
        PROJECT_ROOT / "docs" / "final_status.md",
        PROJECT_ROOT / "docs" / "frontend_handoff_checklist.md",
    ]

    for path in docs:
        assert path.exists()

    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)
    for keyword in [
        "BackendController",
        "PatchReviewCreated",
        "EnvRepairPlanCreated",
        "workspace",
        "score.json",
    ]:
        assert keyword in combined
