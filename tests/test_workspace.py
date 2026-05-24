import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.task_loader import load_benchmark_task
from scicodepilot.eval.workspace import WorkspaceManager


def test_workspace_manager_copies_repo_and_isolates_changes(tmp_path) -> None:
    task = load_benchmark_task("benchmark/tasks/repair_entrypoint_error_005")
    workspace = WorkspaceManager(tmp_path / "workspaces").create_workspace(
        task,
        run_id="test_run",
    )
    source_train = Path(task.repo_dir) / "train.py"
    workspace_train = Path(workspace.workspace_repo_dir) / "train.py"

    assert workspace.task_id == task.task_id
    assert workspace.run_id == "test_run"
    assert workspace_train.exists()

    workspace_train.write_text("changed in workspace\n", encoding="utf-8")

    assert source_train.read_text(encoding="utf-8") != workspace_train.read_text(
        encoding="utf-8"
    )
    assert "mainn()" in source_train.read_text(encoding="utf-8")
