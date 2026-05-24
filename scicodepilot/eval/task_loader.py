import json
from pathlib import Path

from pydantic import BaseModel, Field


class BenchmarkTask(BaseModel):
    """Loaded metadata and resolved paths for one benchmark task."""

    task_id: str
    task_name: str
    category: str
    difficulty: str
    entry_command: str
    task_dir: str
    repo_dir: str
    expected_diagnosis_path: str
    requires: list[str] = Field(default_factory=list)


def load_benchmark_task(task_dir: str | Path) -> BenchmarkTask:
    """Load one benchmark task from its task directory."""
    task_path = Path(task_dir)
    metadata_path = task_path / "metadata.json"

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    expected_diagnosis_path = task_path / metadata["expected_diagnosis_file"]
    repo_dir = task_path / "repo"

    return BenchmarkTask(
        task_id=metadata["task_id"],
        task_name=metadata["task_name"],
        category=metadata["category"],
        difficulty=metadata["difficulty"],
        entry_command=metadata["entry_command"],
        task_dir=str(task_path),
        repo_dir=str(repo_dir),
        expected_diagnosis_path=str(expected_diagnosis_path),
        requires=metadata.get("requires", []),
    )
