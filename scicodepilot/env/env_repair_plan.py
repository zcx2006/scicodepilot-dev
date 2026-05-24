from typing import Literal

from pydantic import BaseModel


class EnvRepairPlan(BaseModel):
    """Structured plan for non-source-code environment or data repairs."""

    task_id: str
    error_type: str
    issue_category: Literal["dependency", "missing_file", "environment", "data"]
    summary: str
    evidence: list[str]
    suggested_actions: list[str]
    verification_command: str | None = None
    confidence: float
    requires_user_action: bool
