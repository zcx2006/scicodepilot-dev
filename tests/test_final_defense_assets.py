from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_final_defense_assets_exist() -> None:
    for path in [
        "docs/defense_outline.md",
        "docs/final_demo_script.md",
        "docs/final_claims_checklist.md",
        "report_assets/tables/final_results_summary.md",
        "report_assets/figures/defense_system_overview.md",
        "scripts/run_final_defense_demo.py",
    ]:
        assert (PROJECT_ROOT / path).exists()


def test_final_results_summary_contains_key_rows() -> None:
    text = read("report_assets/tables/final_results_summary.md")

    assert "Controlled tasks" in text
    assert "Diagnosis pass count" in text
    assert "Memory retrieval top-1 self match" in text
    assert "Public benchmark evaluation" in text
    assert "Real LLM evaluation" in text


def test_final_claims_checklist_contains_required_sections_and_prohibitions() -> None:
    text = read("docs/final_claims_checklist.md")

    assert "Safe Claims" in text
    assert "Prohibited Claims" in text
    assert "SOTA" in text
    assert "Completed SWE-bench" in text
    assert "Real-world generalization" in text


def test_defense_system_overview_contains_mermaid_and_key_nodes() -> None:
    text = read("report_assets/figures/defense_system_overview.md")

    assert "```mermaid" in text
    assert "FailureMemory" in text
    assert "PatchSafetyReviewer" in text
    assert "EnvDoctor" in text
    assert "Memory" in text
    assert "Prompt" in text


def test_final_demo_script_contains_key_commands() -> None:
    text = read("docs/final_demo_script.md")

    assert "run_showcase_demo.py" in text
    assert "export_component_metrics.py" in text
    assert "export_failure_memory_records.py" in text
    assert "evaluate_memory_retrieval.py" in text


def test_run_final_defense_demo_help_succeeds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_final_defense_demo.py"),
            "--help",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Run SciCodePilot final defense demo" in result.stdout


def test_final_report_and_summary_avoid_positive_unsupported_claims() -> None:
    checked_text = "\n".join(
        [
            read("docs/final_report_draft.md"),
            read("report_assets/tables/final_results_summary.md"),
        ]
    )

    for forbidden in [
        "outperforms",
        "state-of-the-art",
        "completed BugsInPy",
        "completed SWE-bench",
    ]:
        assert forbidden not in checked_text
