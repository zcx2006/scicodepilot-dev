from __future__ import annotations

from scicodepilot.memory.record import FailureMemoryRecord, RetrievedFailureMemory


SAFETY_CONSTRAINTS = [
    "no shell execution",
    "no dependency installation",
    "no fake data creation",
    "no absolute paths",
    "no path traversal",
    "no benchmark/test/output modification",
    "patch must still pass PatchSafetyReviewer",
]


def _value(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _record_summary(record: FailureMemoryRecord) -> list[str]:
    return [
        f"record_id: {_value(record.record_id)}",
        f"task_id: {_value(record.task_id)}",
        f"error_type: {_value(record.error_type)}",
        f"failure_category: {_value(record.failure_category)}",
        f"exception_type: {_value(record.exception_type)}",
        f"error_message: {_value(record.error_message)}",
        f"traceback_summary: {_value(record.traceback_summary)}",
        f"root_cause_hypothesis: {_value(record.root_cause_hypothesis)}",
        f"repair_action: {_value(record.repair_action)}",
        f"patch_plan_summary: {_value(record.patch_plan_summary)}",
        f"verification_success: {_value(record.verification_success)}",
        f"score: {_value(record.score)}",
    ]


def build_memory_augmented_patch_prompt(
    current_failure: FailureMemoryRecord,
    retrieved_memories: list[RetrievedFailureMemory],
) -> str:
    """Build a deterministic prompt for future structured patch planning."""

    lines = [
        "You are a memory-augmented structured PatchPlan planner for SciCodePilot.",
        "Return only structured PatchPlan JSON. Do not include markdown fences or commentary.",
        "Required JSON fields: task_id, error_type, target_file, suspected_line, rationale, proposed_change, unified_diff, confidence.",
        "The unified_diff must be a single-file source-code patch for a safe relative target path.",
        "",
        "Safety constraints:",
    ]
    lines.extend(f"- {constraint}" for constraint in SAFETY_CONSTRAINTS)
    lines.extend(
        [
            "",
            "Current failure:",
        ]
    )
    lines.extend(f"- {item}" for item in _record_summary(current_failure))
    lines.extend(["", "Retrieved examples:"])

    if not retrieved_memories:
        lines.append("- None")
    else:
        for index, retrieved in enumerate(retrieved_memories, start=1):
            lines.append(f"Example {index}:")
            lines.append(f"- retrieval_score: {retrieved.score}")
            lines.append(
                "- matched_terms: "
                + (", ".join(retrieved.matched_terms) if retrieved.matched_terms else "None")
            )
            lines.extend(f"- {item}" for item in _record_summary(retrieved.record))

    lines.extend(
        [
            "",
            "Planner instruction:",
            "Use retrieved examples only as compact repair analogies.",
            "Do not copy unsafe paths, shell commands, dependency installs, fake data creation, secrets, or environment variables.",
            "If a safe source-code patch cannot be proposed, return a PatchPlan JSON with low confidence and a rationale explaining the limitation.",
        ]
    )
    return "\n".join(lines) + "\n"
