from __future__ import annotations

from scicodepilot.benchmarks.public_task import PublicBenchmarkTask


PLACEHOLDER_NOTE = "metadata placeholder only; not executed in current report"

_PUBLIC_PILOT_TASKS: tuple[PublicBenchmarkTask, ...] = (
    PublicBenchmarkTask(
        task_id="bugs_in_py_placeholder_001",
        source="bugs_in_py_placeholder",
        repo="example/python-project",
        commit="placeholder-commit",
        issue_or_bug_id="placeholder-bug-001",
        setup_command="python -m pip install -e .",
        test_command="pytest tests/test_placeholder.py",
        expected_failure_type="pytest_failure",
        notes=PLACEHOLDER_NOTE,
    ),
    PublicBenchmarkTask(
        task_id="bugs_in_py_placeholder_002",
        source="bugs_in_py_placeholder",
        repo="example/scientific-python-project",
        commit="placeholder-commit",
        issue_or_bug_id="placeholder-bug-002",
        setup_command="python -m pip install -e .",
        test_command="pytest tests/test_regression_placeholder.py",
        expected_failure_type="assertion_failure",
        notes=PLACEHOLDER_NOTE,
    ),
    PublicBenchmarkTask(
        task_id="swebench_lite_placeholder_001",
        source="swebench_lite_placeholder",
        repo="example/issue-level-python-project",
        commit="placeholder-commit",
        issue_or_bug_id="placeholder-instance-001",
        setup_command="python -m pip install -e .",
        test_command="pytest tests/test_issue_placeholder.py",
        expected_failure_type="issue_level_repair",
        notes=PLACEHOLDER_NOTE,
    ),
)


def list_public_pilot_tasks() -> list[PublicBenchmarkTask]:
    """Return metadata placeholders for future public benchmark pilot tasks."""

    return list(_PUBLIC_PILOT_TASKS)


def get_public_pilot_task(task_id: str) -> PublicBenchmarkTask | None:
    """Return a public pilot placeholder task by id, or None when absent."""

    for task in _PUBLIC_PILOT_TASKS:
        if task.task_id == task_id:
            return task
    return None
