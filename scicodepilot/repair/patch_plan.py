from pydantic import BaseModel, Field


class PatchPlan(BaseModel):
    """A proposed repair plan and diff draft that has not been applied."""

    task_id: str
    error_type: str
    target_file: str
    suspected_line: int | None
    rationale: str
    proposed_change: str
    unified_diff: str
    confidence: float
    safety_notes: list[str] = Field(default_factory=list)
