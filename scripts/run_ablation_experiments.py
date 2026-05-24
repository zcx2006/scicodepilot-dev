import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SUMMARY_KEYS = {
    "mode",
    "total_tasks",
    "diagnosis_pass_count",
    "patch_plan_count",
    "patch_review_count",
    "patch_review_blocked_count",
    "patch_applied_count",
    "verification_success_count",
    "env_repair_plan_count",
    "scored_task_count",
    "total_score",
    "average_score",
    "output_dir",
}


def coerce_value(value: str) -> int | float | str:
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def tail(text: str, line_count: int = 40) -> str:
    return "\n".join(text.splitlines()[-line_count:])


def parse_summary(stdout: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in SUMMARY_KEYS:
            parsed[key] = coerce_value(value)

    pytest_match = re.search(r"(\d+)\s+passed", stdout)
    if pytest_match:
        parsed["safety_case_pass_count"] = int(pytest_match.group(1))

    return parsed


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
        "stdout_tail": tail(result.stdout),
        "stderr_tail": tail(result.stderr),
        "parsed_summary": parse_summary(result.stdout),
        "success": result.returncode == 0,
    }


def build_experiments(include_safety: bool) -> list[tuple[str, list[str], dict[str, str] | None]]:
    python = sys.executable
    suite_script = str(PROJECT_ROOT / "scripts" / "run_benchmark_suite.py")
    experiments: list[tuple[str, list[str], dict[str, str] | None]] = [
        (
            "diagnosis_only",
            [python, suite_script, "--mode", "diagnosis"],
            None,
        ),
        (
            "repair_without_apply",
            [python, suite_script, "--mode", "repair"],
            None,
        ),
        (
            "full_rule_based_repair",
            [python, suite_script, "--mode", "repair", "--confirm-apply"],
            None,
        ),
        (
            "mock_llm_repair",
            [
                python,
                suite_script,
                "--mode",
                "repair",
                "--confirm-apply",
                "--use-llm-planner",
            ],
            {"SCICODEPILOT_LLM_PROVIDER": "mock"},
        ),
    ]

    if include_safety:
        experiments.append(
            (
                "safety_stress_cases",
                [python, "-m", "pytest", "tests/test_patch_safety_reviewer.py", "-q"],
                None,
            )
        )

    return experiments


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run SciCodePilot ablation experiments for report tables."
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run the default benchmark ablations. This is the default behavior.",
    )
    parser.add_argument("--include-safety", action="store_true")
    parser.add_argument(
        "--output-dir",
        help="Optional explicit output directory. Defaults to outputs/ablations/<timestamp>.",
    )
    args = parser.parse_args()

    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = PROJECT_ROOT / output_dir
        timestamp = output_dir.name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = PROJECT_ROOT / "outputs" / "ablations" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    experiments = []
    for name, command, env in build_experiments(include_safety=args.include_safety):
        print(f"Running ablation: {name}")
        record = run_command(name, command, env=env)
        experiments.append(record)
        print(f"  return_code={record['return_code']} success={record['success']}")

    summary = {
        "timestamp": timestamp,
        "output_dir": str(output_dir),
        "quick": True,
        "include_safety": args.include_safety,
        "experiments": experiments,
    }
    summary_path = output_dir / "ablation_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"ablation_summary_path: {summary_path}")

    if any(not experiment["success"] for experiment in experiments):
        sys.exit(1)


if __name__ == "__main__":
    main()
