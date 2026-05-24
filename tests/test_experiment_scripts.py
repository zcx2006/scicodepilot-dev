import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_experiment_scripts_exist() -> None:
    assert (PROJECT_ROOT / "scripts" / "run_experiments.py").exists()
    assert (PROJECT_ROOT / "scripts" / "export_results_table.py").exists()


def test_run_experiments_help_succeeds() -> None:
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "run_experiments.py"), "--help"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--include-mock-llm" in result.stdout


def test_export_results_table_help_succeeds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "export_results_table.py"),
            "--help",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--latest" in result.stdout
