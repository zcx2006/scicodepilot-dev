import json
from pathlib import Path

from scicodepilot.eval.score_result import ScoreResult
from scicodepilot.eval.task_loader import BenchmarkTask
from scicodepilot.events.bus import EventBus
from scicodepilot.tools.shell_tool import ShellTool


class HiddenEvaluator:
    """Minimal hidden evaluator that runs the task command in a workspace."""

    async def evaluate(
        self,
        task: BenchmarkTask,
        workspace_repo_dir: str,
    ) -> ScoreResult:
        """Run the benchmark entry command and write score.json."""
        result = await ShellTool(EventBus()).run(
            task_id=task.task_id,
            command=task.entry_command,
            cwd=workspace_repo_dir,
        )
        success = result.return_code == 0
        score_path = str(Path(workspace_repo_dir).parent / "score.json")
        score = ScoreResult(
            task_id=task.task_id,
            success=success,
            score=1.0 if success else 0.0,
            verification_command=task.entry_command,
            return_code=result.return_code,
            message=(
                "Hidden evaluation command succeeded."
                if success
                else "Hidden evaluation command failed."
            ),
            score_path=score_path,
            checks={"command_success": success},
        )
        Path(score_path).write_text(
            json.dumps(self._model_to_dict(score), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return score

    def _model_to_dict(self, model) -> dict:
        if hasattr(model, "model_dump"):
            return model.model_dump()
        return model.dict()
