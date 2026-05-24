from typing import Literal

from pydantic import BaseModel


class PatchReview(BaseModel):
    """Static safety review result for a proposed patch plan."""

    task_id: str
    error_type: str
    target_file: str
    approved: bool
    blocked: bool
    risk_level: Literal["low", "medium", "high"]
    reasons: list[str]
    warnings: list[str]
    reviewer: str = "rule_based_patch_safety_reviewer"
