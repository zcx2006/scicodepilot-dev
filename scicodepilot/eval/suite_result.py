from pydantic import BaseModel


class BenchmarkCaseResult(BaseModel):
    """One benchmark task result in diagnosis or repair mode."""

    task_id: str
    mode: str
    command_success: bool | None = None
    parsed_error_type: str | None = None
    diagnosis_passed: bool | None = None
    patch_plan_generated: bool | None = None
    patch_applied: bool | None = None
    verification_success: bool | None = None
    verification_return_code: int | None = None
    score: float | None = None
    score_path: str | None = None
    workspace_repo_dir: str | None = None
    env_repair_plan_generated: bool | None = None
    env_issue_category: str | None = None
    patch_review_approved: bool | None = None
    patch_review_blocked: bool | None = None
    patch_review_risk_level: str | None = None
    message: str


class BenchmarkSuiteSummary(BaseModel):
    """Aggregated counters for a benchmark suite run."""

    total_tasks: int
    mode: str
    diagnosis_pass_count: int
    patch_plan_count: int
    patch_applied_count: int
    verification_success_count: int
    total_score: float
    average_score: float
    scored_task_count: int
    env_repair_plan_count: int = 0
    patch_review_count: int = 0
    patch_review_blocked_count: int = 0
