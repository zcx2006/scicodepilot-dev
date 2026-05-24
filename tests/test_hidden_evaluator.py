import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.hidden_evaluator import HiddenEvaluator
from scicodepilot.eval.task_loader import load_benchmark_task
from scicodepilot.eval.workspace import WorkspaceManager


@pytest.mark.asyncio
async def test_hidden_evaluator_scores_fixed_workspace_success(tmp_path) -> None:
    task = load_benchmark_task("benchmark/tasks/repair_entrypoint_error_005")
    workspace = WorkspaceManager(tmp_path / "workspaces").create_workspace(
        task,
        run_id="fixed",
    )
    train_path = Path(workspace.workspace_repo_dir) / "train.py"
    train_path.write_text(
        train_path.read_text(encoding="utf-8").replace("mainn()", "main()"),
        encoding="utf-8",
    )

    score = await HiddenEvaluator().evaluate(task, workspace.workspace_repo_dir)

    assert score.success is True
    assert score.score == 1.0
    assert score.return_code == 0
    assert score.score_path is not None
    data = json.loads(Path(score.score_path).read_text(encoding="utf-8"))
    assert data["success"] is True
    assert data["score"] == 1.0


@pytest.mark.asyncio
async def test_hidden_evaluator_scores_unfixed_workspace_failure(tmp_path) -> None:
    task = load_benchmark_task("benchmark/tasks/repair_entrypoint_error_005")
    workspace = WorkspaceManager(tmp_path / "workspaces").create_workspace(
        task,
        run_id="broken",
    )

    score = await HiddenEvaluator().evaluate(task, workspace.workspace_repo_dir)

    assert score.success is False
    assert score.score == 0.0
    assert score.return_code != 0
    assert score.score_path is not None
    data = json.loads(Path(score.score_path).read_text(encoding="utf-8"))
    assert data["success"] is False
    assert data["score"] == 0.0
