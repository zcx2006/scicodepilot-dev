import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_ablation_scripts_exist() -> None:
    assert (PROJECT_ROOT / "scripts" / "run_ablation_experiments.py").exists()
    assert (PROJECT_ROOT / "scripts" / "export_ablation_tables.py").exists()


def test_run_ablation_experiments_help_succeeds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_ablation_experiments.py"),
            "--help",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--include-safety" in result.stdout


def test_export_ablation_tables_help_succeeds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "export_ablation_tables.py"),
            "--help",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--latest" in result.stdout


def test_ablation_study_doc_exists_and_names_variants() -> None:
    text = (PROJECT_ROOT / "docs" / "ablation_study.md").read_text(
        encoding="utf-8"
    )

    assert "diagnosis_only" in text
    assert "full_rule_based_repair" in text
    assert "mock_llm_repair" in text


def test_results_analysis_doc_exists_and_contains_core_terms() -> None:
    text = (PROJECT_ROOT / "docs" / "results_analysis.md").read_text(
        encoding="utf-8"
    )

    assert "10-task" in text
    assert "average_score" in text
    assert "safety" in text.lower()
