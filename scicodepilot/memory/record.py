from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class FailureMemoryRecord:
    """Serializable historical failure/repair memory record."""

    record_id: str
    task_id: str | None = None
    error_type: str | None = None
    failure_category: str | None = None
    command: str | None = None
    exception_type: str | None = None
    error_message: str | None = None
    traceback_summary: str | None = None
    root_cause_hypothesis: str | None = None
    repair_action: str | None = None
    patch_plan_summary: str | None = None
    verification_success: bool | None = None
    score: float | None = None
    created_from: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id or not self.record_id.strip():
            raise ValueError("record_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FailureMemoryRecord":
        """Build a memory record from a dictionary."""

        allowed_fields = set(cls.__dataclass_fields__)
        filtered = {key: value for key, value in data.items() if key in allowed_fields}
        if "record_id" not in filtered:
            raise ValueError("record_id must be non-empty")
        if "metadata" not in filtered or filtered["metadata"] is None:
            filtered["metadata"] = {}
        if not isinstance(filtered["metadata"], dict):
            raise ValueError("metadata must be a dictionary")
        return cls(**filtered)


@dataclass(frozen=True)
class RetrievedFailureMemory:
    """A retrieved memory record with deterministic similarity metadata."""

    record: FailureMemoryRecord
    score: float
    matched_terms: list[str]
