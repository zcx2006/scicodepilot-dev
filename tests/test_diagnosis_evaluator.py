import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.diagnosis_evaluator import (
    ExpectedDiagnosis,
    evaluate_diagnosis,
)
from scicodepilot.memory.failure_memory import FailureMemory
from scicodepilot.tools.traceback_parser import ParsedError


def make_expected(root_cause_keywords: list[str] | None = None) -> ExpectedDiagnosis:
    return ExpectedDiagnosis(
        expected_error_type="tensor_shape",
        expected_summary_keywords=["tensor shape mismatch"],
        expected_root_cause_keywords=root_cause_keywords
        or ["feature dimension", "downstream layer"],
        expected_repair_action_keywords=["inspect", "align"],
    )


def make_failure_memory() -> FailureMemory:
    return FailureMemory(
        error_type="tensor_shape",
        evidence=["RuntimeError ..."],
        root_cause_hypothesis=(
            "The tensor feature dimension used in matrix multiplication is "
            "inconsistent with the expected input dimension of the downstream layer."
        ),
        repair_action=(
            "Inspect the tensor shape before the failing matrix multiplication and "
            "align the downstream layer input dimension with the actual upstream "
            "feature dimension."
        ),
    )


def test_evaluate_expected_tensor_shape_diagnosis_passes() -> None:
    parsed_error = ParsedError(
        error_type="tensor_shape",
        summary=(
            "The program failed due to a tensor shape mismatch during tensor "
            "computation."
        ),
        evidence=["RuntimeError ..."],
    )

    result = evaluate_diagnosis(parsed_error, make_failure_memory(), make_expected())

    assert result.passed is True
    assert all(result.checks.values())


def test_evaluate_wrong_error_type_fails() -> None:
    parsed_error = ParsedError(
        error_type="dtype_mismatch",
        summary=(
            "The program failed due to a tensor shape mismatch during tensor "
            "computation."
        ),
        evidence=["RuntimeError ..."],
    )

    result = evaluate_diagnosis(parsed_error, make_failure_memory(), make_expected())

    assert result.passed is False
    assert result.checks["error_type_match"] is False


def test_evaluate_missing_keyword_fails() -> None:
    parsed_error = ParsedError(
        error_type="tensor_shape",
        summary=(
            "The program failed due to a tensor shape mismatch during tensor "
            "computation."
        ),
        evidence=["RuntimeError ..."],
    )
    expected = make_expected(["feature dimension", "classifier unicorn"])

    result = evaluate_diagnosis(parsed_error, make_failure_memory(), expected)

    assert result.passed is False
    assert result.checks["root_cause_keywords_match"] is False
