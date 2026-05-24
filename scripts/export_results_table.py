import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TABLE_FIELDS = [
    "total_tasks",
    "diagnosis_pass_count",
    "patch_plan_count",
    "patch_review_count",
    "patch_review_blocked_count",
    "patch_applied_count",
    "verification_success_count",
    "env_repair_plan_count",
    "average_score",
]


def find_latest_experiment_dir(root: Path) -> Path:
    candidates = [
        path for path in root.iterdir() if path.is_dir() and (path / "summary.json").exists()
    ]
    if not candidates:
        raise FileNotFoundError(f"No experiment summaries found under {root}")
    return sorted(candidates)[-1]


def format_value(summary: dict[str, Any], field: str) -> str:
    value = summary.get(field, "-")
    return str(value)


def build_table(summary_data: dict[str, Any]) -> str:
    headers = ["Experiment", *TABLE_FIELDS]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for experiment in summary_data.get("experiments", []):
        parsed_summary = experiment.get("parsed_summary") or {}
        row = [
            experiment.get("name", "-"),
            *[format_value(parsed_summary, field) for field in TABLE_FIELDS],
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export experiment summary as markdown.")
    parser.add_argument("--input", help="Path to an experiment summary.json file.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest outputs/experiments/<timestamp>/summary.json.",
    )
    parser.add_argument("--experiments-root", default="outputs/experiments")
    args = parser.parse_args()

    if args.latest:
        experiment_dir = find_latest_experiment_dir(PROJECT_ROOT / args.experiments_root)
        summary_path = experiment_dir / "summary.json"
    elif args.input:
        summary_path = Path(args.input)
        if not summary_path.is_absolute():
            summary_path = PROJECT_ROOT / summary_path
        experiment_dir = summary_path.parent
    else:
        parser.error("Use --latest or --input <summary.json>.")

    summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
    table = build_table(summary_data)
    output_path = experiment_dir / "results_table.md"
    output_path.write_text(table, encoding="utf-8")
    print(f"results_table_path: {output_path}")


if __name__ == "__main__":
    main()
