from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scicodepilot.benchmarks.public_registry import (
    get_public_pilot_task,
    list_public_pilot_tasks,
)
from scicodepilot.benchmarks.public_task import PublicBenchmarkTask


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_list_public_pilot_tasks_returns_placeholders() -> None:
    tasks = list_public_pilot_tasks()

    assert tasks
    assert all(isinstance(task, PublicBenchmarkTask) for task in tasks)
    assert all("placeholder only" in task.notes for task in tasks)


def test_get_public_pilot_task_finds_existing_task() -> None:
    task = list_public_pilot_tasks()[0]

    found = get_public_pilot_task(task.task_id)

    assert found == task


def test_get_public_pilot_task_returns_none_for_unknown_task() -> None:
    assert get_public_pilot_task("unknown-public-task") is None


def test_list_public_pilot_tasks_script_outputs_placeholder_info() -> None:
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "list_public_pilot_tasks.py")],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "bugs_in_py_placeholder" in result.stdout
    assert "swebench_lite_placeholder" in result.stdout
    assert "metadata placeholder only; not executed in current report" in result.stdout


def test_public_benchmark_plan_doc_contains_scope_terms() -> None:
    text = (PROJECT_ROOT / "docs" / "public_benchmark_plan.md").read_text(
        encoding="utf-8"
    )

    assert "internal controlled benchmark" in text
    assert "not a SOTA comparison" in text
    assert "BugsInPy" in text
    assert "SWE-bench Lite" in text
