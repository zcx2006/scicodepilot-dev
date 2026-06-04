#!/usr/bin/env python3
"""Run the curated SciCodePilot final defense demo."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, command: list[str]) -> subprocess.CompletedProcess[str]:
    print()
    print(f"=== {name} ===")
    print("$ " + " ".join(command))
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(f"{name} failed with return code {result.returncode}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SciCodePilot final defense demo.")
    parser.parse_args()

    python = sys.executable
    print("SciCodePilot Final Defense Demo")
    print("scope: internal controlled benchmark and component-level assets")

    run_step("Showcase demo", [python, "scripts/run_showcase_demo.py"])
    run_step(
        "Export component metrics",
        [python, "scripts/export_component_metrics.py", "--latest"],
    )
    run_step(
        "Export failure memory records",
        [python, "scripts/export_failure_memory_records.py", "--latest"],
    )
    memory_demo = run_step(
        "Run memory retrieval demo",
        [python, "scripts/run_memory_retrieval_demo.py"],
    )
    memory_eval = run_step(
        "Evaluate memory retrieval",
        [python, "scripts/evaluate_memory_retrieval.py", "--latest"],
    )

    print()
    print("=== Final Defense Summary ===")
    print("component_metrics_table: report_assets/tables/component_metrics.md")
    print("final_results_summary_table: report_assets/tables/final_results_summary.md")
    print("memory_retrieval_eval_table: report_assets/tables/memory_retrieval_eval.md")
    for line in memory_demo.stdout.splitlines():
        if line.startswith("memory_retrieval_output:"):
            print(line)
    for line in memory_eval.stdout.splitlines():
        if line.startswith("memory_retrieval_eval_output:"):
            print(line)
    print("manual_test_command: pytest -q")
    print("public_benchmark_executed: false")
    print("real_llm_called: false")
    print("external_baseline_comparison: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
