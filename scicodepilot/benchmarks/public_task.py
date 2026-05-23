from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicBenchmarkTask:
    """Metadata for a future public benchmark pilot task."""

    task_id: str
    source: str
    repo: str
    commit: str
    issue_or_bug_id: str
    setup_command: str
    test_command: str
    expected_failure_type: str
    notes: str
