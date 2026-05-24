from pydantic import BaseModel


class ScoreResult(BaseModel):
    """Hidden evaluator score for a repaired workspace."""

    task_id: str
    success: bool
    score: float
    verification_command: str
    return_code: int | None
    message: str
    score_path: str | None
    checks: dict[str, bool]
