import json
from pathlib import Path

from pydantic import BaseModel

from scicodepilot.memory.failure_memory import FailureMemory
from scicodepilot.tools.traceback_parser import ParsedError


class ExpectedDiagnosis(BaseModel):
    """Minimum expected diagnosis criteria for a benchmark task."""

    expected_error_type: str
    expected_summary_keywords: list[str]
    expected_root_cause_keywords: list[str]
    expected_repair_action_keywords: list[str]


class DiagnosisEvaluationResult(BaseModel):
    """Boolean checks and readable messages for a diagnosis evaluation."""

    passed: bool
    checks: dict[str, bool]
    messages: list[str]


def load_expected_diagnosis(path: str | Path) -> ExpectedDiagnosis:
    """Load expected diagnosis criteria from JSON."""
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    return ExpectedDiagnosis(**data)


def find_missing_keywords(text: str, expected_keywords: list[str]) -> list[str]:
    """Return expected keywords that are absent, using case-insensitive matching."""
    lowered_text = text.lower()
    return [
        keyword
        for keyword in expected_keywords
        if keyword.lower() not in lowered_text
    ]


def build_check_message(check_name: str, passed: bool, missing: list[str] | None = None) -> str:
    """Create a compact human-readable message for one check."""
    if passed:
        return f"{check_name}: passed"

    if missing is None:
        return f"{check_name}: failed"

    return f"{check_name}: failed; missing={missing}"


def evaluate_diagnosis(
    parsed_error: ParsedError,
    failure_memory: FailureMemory,
    expected: ExpectedDiagnosis,
) -> DiagnosisEvaluationResult:
    """Compare an actual diagnosis with benchmark expectations."""
    summary_missing = find_missing_keywords(
        parsed_error.summary,
        expected.expected_summary_keywords,
    )
    root_cause_missing = find_missing_keywords(
        failure_memory.root_cause_hypothesis,
        expected.expected_root_cause_keywords,
    )
    repair_action_missing = find_missing_keywords(
        failure_memory.repair_action,
        expected.expected_repair_action_keywords,
    )

    checks = {
        "error_type_match": parsed_error.error_type == expected.expected_error_type,
        "summary_keywords_match": not summary_missing,
        "root_cause_keywords_match": not root_cause_missing,
        "repair_action_keywords_match": not repair_action_missing,
    }

    messages = [
        build_check_message("error_type_match", checks["error_type_match"]),
        build_check_message(
            "summary_keywords_match",
            checks["summary_keywords_match"],
            summary_missing,
        ),
        build_check_message(
            "root_cause_keywords_match",
            checks["root_cause_keywords_match"],
            root_cause_missing,
        ),
        build_check_message(
            "repair_action_keywords_match",
            checks["repair_action_keywords_match"],
            repair_action_missing,
        ),
    ]

    return DiagnosisEvaluationResult(
        passed=all(checks.values()),
        checks=checks,
        messages=messages,
    )
