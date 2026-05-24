from scicodepilot.memory.failure_memory import FailureMemory
from scicodepilot.tools.traceback_parser import ParsedError


def build_patch_prompt(
    task_id: str,
    parsed_error: ParsedError,
    failure_memory: FailureMemory,
    source_code: str,
    target_file: str,
) -> str:
    """Build a constrained prompt for optional LLM patch planning."""
    return (
        "You are an optional patch planner for SciCodePilot.\n"
        "Only propose a source-code patch when the error is repairable in the target file.\n"
        "Do not install dependencies, create data files, or execute commands.\n"
        "Return only JSON, with no markdown fences or commentary.\n"
        "Required JSON fields: target_file, rationale, proposed_change, unified_diff, confidence.\n"
        "The unified_diff must be a simple single-file diff for train.py.\n"
        "\n"
        f"task_id: {task_id}\n"
        f"target_file: {target_file}\n"
        f"error_type: {parsed_error.error_type}\n"
        f"error_summary: {parsed_error.summary}\n"
        f"evidence: {parsed_error.evidence}\n"
        f"root_cause_hypothesis: {failure_memory.root_cause_hypothesis}\n"
        f"repair_action: {failure_memory.repair_action}\n"
        "\n"
        "source_code:\n"
        "```python\n"
        f"{source_code}\n"
        "```\n"
    )
