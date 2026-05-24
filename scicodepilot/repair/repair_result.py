from pydantic import BaseModel


class RepairResult(BaseModel):
    """Result of applying one patch plan and running a verification command."""

    task_id: str
    patch_applied: bool
    target_file: str | None
    verification_command: str
    verification_success: bool
    verification_return_code: int | None
    message: str
    patch_plan_generated: bool = False
    requires_confirmation: bool = False
    confirmation_granted: bool = False
    score: float | None = None
    score_path: str | None = None
    workspace_repo_dir: str | None = None
    env_repair_plan_generated: bool | None = None
    env_issue_category: str | None = None
    patch_review_approved: bool | None = None
    patch_review_blocked: bool | None = None
    patch_review_risk_level: str | None = None
