from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base fields shared by every event in the demo event stream."""

    timestamp: datetime = Field(default_factory=datetime.now)


class TaskStarted(EventBase):
    """Emitted when a task begins."""

    type: Literal["TaskStarted"] = "TaskStarted"
    task_id: str
    task_name: str


class PlanCreated(EventBase):
    """Emitted after the agent creates a simple execution plan."""

    type: Literal["PlanCreated"] = "PlanCreated"
    task_id: str
    steps: list[str]


class StepStarted(EventBase):
    """Emitted when the agent starts one step from the plan."""

    type: Literal["StepStarted"] = "StepStarted"
    task_id: str
    step_index: int
    step_name: str


class CommandStarted(EventBase):
    """Emitted before a command would be executed."""

    type: Literal["CommandStarted"] = "CommandStarted"
    task_id: str
    command: str


class CommandOutput(EventBase):
    """Emitted for simulated stdout or stderr output from a command."""

    type: Literal["CommandOutput"] = "CommandOutput"
    task_id: str
    stream: Literal["stdout", "stderr"]
    content: str


class CommandFinished(EventBase):
    """Emitted after a command process exits."""

    type: Literal["CommandFinished"] = "CommandFinished"
    task_id: str
    command: str
    return_code: int
    success: bool


class ErrorDetected(EventBase):
    """Emitted when the demo detects a structured runtime error."""

    type: Literal["ErrorDetected"] = "ErrorDetected"
    task_id: str
    error_type: str
    summary: str
    evidence: list[str]


class FailureMemoryCreated(EventBase):
    """Emitted when the demo turns an error into reusable failure memory."""

    type: Literal["FailureMemoryCreated"] = "FailureMemoryCreated"
    task_id: str
    error_type: str
    evidence: list[str]
    root_cause_hypothesis: str
    repair_action: str


class EnvRepairPlanCreated(EventBase):
    """Emitted when an environment or data repair plan is generated."""

    type: Literal["EnvRepairPlanCreated"] = "EnvRepairPlanCreated"
    task_id: str
    error_type: str
    issue_category: str
    summary: str
    suggested_actions: list[str]
    requires_user_action: bool
    confidence: float


class PatchApplied(EventBase):
    """Emitted after the system attempts to apply a patch plan."""

    type: Literal["PatchApplied"] = "PatchApplied"
    task_id: str
    target_file: str | None
    success: bool
    message: str
    unified_diff: str | None = None


class PatchProposed(EventBase):
    """Emitted when the system generates a patch plan but has not applied it."""

    type: Literal["PatchProposed"] = "PatchProposed"
    task_id: str
    target_file: str
    suspected_line: int | None
    confidence: float
    proposed_change: str
    unified_diff: str


class PatchReviewCreated(EventBase):
    """Emitted after a patch plan passes through the static safety reviewer."""

    type: Literal["PatchReviewCreated"] = "PatchReviewCreated"
    task_id: str
    approved: bool
    blocked: bool
    risk_level: str
    reasons: list[str]
    warnings: list[str]


class PatchApprovalRequired(EventBase):
    """Emitted when policy requires explicit approval before applying a patch."""

    type: Literal["PatchApprovalRequired"] = "PatchApprovalRequired"
    task_id: str
    target_file: str
    message: str
    unified_diff: str


class VerificationStarted(EventBase):
    """Emitted before running a post-patch verification command."""

    type: Literal["VerificationStarted"] = "VerificationStarted"
    task_id: str
    command: str
    cwd: str | None = None


class VerificationFinished(EventBase):
    """Emitted after the post-patch verification command finishes."""

    type: Literal["VerificationFinished"] = "VerificationFinished"
    task_id: str
    command: str
    return_code: int
    success: bool
    summary: str


class TaskFinished(EventBase):
    """Emitted when the task is complete."""

    type: Literal["TaskFinished"] = "TaskFinished"
    task_id: str
    status: Literal["success", "failed", "demo_finished"]
    summary: str


# Python 3.10 supports this compact union syntax.
Event = (
    TaskStarted
    | PlanCreated
    | StepStarted
    | CommandStarted
    | CommandOutput
    | CommandFinished
    | ErrorDetected
    | FailureMemoryCreated
    | EnvRepairPlanCreated
    | PatchProposed
    | PatchReviewCreated
    | PatchApprovalRequired
    | PatchApplied
    | VerificationStarted
    | VerificationFinished
    | TaskFinished
)
