from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_research_questions_doc_contains_core_terms() -> None:
    text = (PROJECT_ROOT / "docs" / "research_questions.md").read_text(
        encoding="utf-8"
    )

    assert "structured failure memory" in text.lower()
    assert "EnvDoctor" in text
    assert "PatchSafetyReviewer" in text


def test_experiment_protocol_doc_contains_metrics() -> None:
    text = (PROJECT_ROOT / "docs" / "experiment_protocol.md").read_text(
        encoding="utf-8"
    )

    assert "average_score" in text
    assert "patch_review_count" in text
    assert "env_repair_plan_count" in text


def test_failure_taxonomy_doc_contains_error_types() -> None:
    text = (PROJECT_ROOT / "docs" / "failure_taxonomy.md").read_text(
        encoding="utf-8"
    )

    assert "tensor_shape" in text
    assert "missing_module" in text
    assert "missing_file" in text


def test_safety_cases_doc_contains_blocked_cases() -> None:
    text = (PROJECT_ROOT / "docs" / "safety_cases.md").read_text(encoding="utf-8")

    assert "path traversal" in text
    assert "pip install" in text
    assert "rm -rf" in text
