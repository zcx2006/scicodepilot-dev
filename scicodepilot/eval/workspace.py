import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel

from scicodepilot.eval.task_loader import BenchmarkTask


class WorkspaceInfo(BaseModel):
    """Resolved paths for one isolated benchmark workspace."""

    task_id: str
    run_id: str
    source_repo_dir: str
    workspace_root: str
    workspace_repo_dir: str


class WorkspaceManager:
    """Create per-run workspace copies of benchmark repos."""

    def __init__(self, workspace_root: str | Path = "outputs/workspaces") -> None:
        self.workspace_root = Path(workspace_root)

    def create_workspace(
        self,
        task: BenchmarkTask,
        run_id: str | None = None,
    ) -> WorkspaceInfo:
        """Copy task.repo_dir into outputs/workspaces/<run_id>/<task_id>/repo."""
        resolved_run_id = run_id or self._new_run_id()
        task_workspace_root = self.workspace_root / resolved_run_id / task.task_id
        workspace_repo_dir = task_workspace_root / "repo"

        if task_workspace_root.exists():
            shutil.rmtree(task_workspace_root)

        task_workspace_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(task.repo_dir, workspace_repo_dir)

        return WorkspaceInfo(
            task_id=task.task_id,
            run_id=resolved_run_id,
            source_repo_dir=str(Path(task.repo_dir)),
            workspace_root=str(task_workspace_root),
            workspace_repo_dir=str(workspace_repo_dir),
        )

    def _new_run_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{uuid4().hex[:8]}"
