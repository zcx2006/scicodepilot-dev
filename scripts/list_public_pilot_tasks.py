#!/usr/bin/env python3
"""List public benchmark pilot placeholder tasks."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.benchmarks.public_registry import list_public_pilot_tasks


def build_table() -> str:
    headers = ["Task ID", "Source", "Repo", "Expected Failure Type", "Notes"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for task in list_public_pilot_tasks():
        row = [
            task.task_id,
            task.source,
            task.repo,
            task.expected_failure_type,
            task.notes,
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    print(build_table(), end="")


if __name__ == "__main__":
    main()
