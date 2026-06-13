from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_doc(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_showcase_demo_script_exists_and_runs() -> None:
    script = PROJECT_ROOT / "scripts" / "run_showcase_demo.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert script.exists()
    assert result.returncode == 0
    assert "FailureMemory" in result.stdout
    assert "PatchReview" in result.stdout
    assert "EnvRepairPlan" in result.stdout
    assert "Safety stress summary" in result.stdout


def test_demo_transcript_contains_required_terms() -> None:
    text = read_doc("docs/demo_transcript.md")

    assert "FailureMemory" in text
    assert "PatchReview" in text
    assert "EnvRepairPlan" in text
    assert "reproducibility manifest" in text


def test_contribution_comparison_contains_comparison_subjects() -> None:
    text = read_doc("docs/contribution_comparison.md")

    assert "naive LLM patch script" in text
    assert "SciCodePilot" in text


def test_contribution_comparison_avoids_false_claims() -> None:
    text = read_doc("docs/contribution_comparison.md")
    forbidden_claims = [
        "SOTA",
        "outperforms SWE-agent",
        "completed SWE-bench",
        "completed BugsInPy",
    ]

    for claim in forbidden_claims:
        assert claim not in text


def test_benchmark_distribution_asset_exists_and_contains_counts() -> None:
    text = read_doc("report_assets/figures/benchmark_distribution.md")

    assert "source-code repair tasks: 8" in text
    assert "env/data routing tasks: 2" in text
