import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_summary_from_stdout(stdout: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in {
            "mode",
            "total_tasks",
            "diagnosis_pass_count",
            "patch_plan_count",
            "patch_review_count",
            "patch_review_blocked_count",
            "patch_applied_count",
            "verification_success_count",
            "scored_task_count",
            "env_repair_plan_count",
            "total_score",
            "average_score",
            "output_dir",
        }:
            parsed[key] = coerce_value(value)
    return parsed


def coerce_value(value: str) -> int | float | str:
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def stdout_tail(stdout: str, line_count: int = 40) -> str:
    return "\n".join(stdout.splitlines()[-line_count:])


def run_command(name: str, command: list[str], env: dict[str, str] | None = None) -> dict:
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=run_env,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "name": name,
        "command": " ".join(command),
        "return_code": result.returncode,
        "stdout_tail": stdout_tail(result.stdout),
        "stderr_tail": stdout_tail(result.stderr),
        "parsed_summary": parse_summary_from_stdout(result.stdout),
    }


def build_experiments(args) -> list[tuple[str, list[str], dict[str, str] | None]]:
    python = sys.executable
    suite_script = str(PROJECT_ROOT / "scripts" / "run_benchmark_suite.py")
    experiments: list[tuple[str, list[str], dict[str, str] | None]] = [
        (
            "diagnosis_suite",
            [python, suite_script, "--mode", "diagnosis"],
            None,
        ),
        (
            "repair_without_apply",
            [python, suite_script, "--mode", "repair"],
            None,
        ),
        (
            "repair_with_confirm_apply",
            [python, suite_script, "--mode", "repair", "--confirm-apply"],
            None,
        ),
    ]

    if args.include_mock_llm:
        experiments.append(
            (
                "mock_llm_repair_with_confirm_apply",
                [
                    python,
                    suite_script,
                    "--mode",
                    "repair",
                    "--confirm-apply",
                    "--use-llm-planner",
                ],
                {"SCICODEPILOT_LLM_PROVIDER": "mock"},
            )
        )

    if args.include_safety_cases:
        experiments.append(
            (
                "patch_safety_reviewer_tests",
                [python, "-m", "pytest", "tests/test_patch_safety_reviewer.py", "-q"],
                None,
            )
        )

    return experiments


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible SciCodePilot experiments.")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run the default quick experiment set. This is currently the default.",
    )
    parser.add_argument("--include-mock-llm", action="store_true")
    parser.add_argument("--include-safety-cases", action="store_true")
    parser.add_argument("--output-root", default="outputs/experiments")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / args.output_root / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    experiments = []
    for name, command, env in build_experiments(args):
        print(f"Running experiment: {name}")
        record = run_command(name, command, env=env)
        experiments.append(record)
        print(f"  return_code={record['return_code']}")

    summary = {
        "timestamp": timestamp,
        "output_dir": str(output_dir),
        "quick": True,
        "include_mock_llm": args.include_mock_llm,
        "include_safety_cases": args.include_safety_cases,
        "experiments": experiments,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"summary_path: {summary_path}")

    failed = [record for record in experiments if record["return_code"] != 0]
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
