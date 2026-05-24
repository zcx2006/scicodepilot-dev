import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TABLE_COLUMNS = [
    ("total_tasks", "Total Tasks"),
    ("diagnosis_pass_count", "Diagnosis Pass"),
    ("patch_plan_count", "Patch Plans"),
    ("env_repair_plan_count", "Env Plans"),
    ("patch_review_count", "Patch Reviews"),
    ("patch_review_blocked_count", "Blocked Reviews"),
    ("patch_applied_count", "Applied Patches"),
    ("verification_success_count", "Verification Success"),
    ("scored_task_count", "Scored Tasks"),
    ("average_score", "Average Score"),
]


def find_latest_ablation_dir(root: Path) -> Path:
    candidates = [
        path
        for path in root.iterdir()
        if path.is_dir() and (path / "ablation_summary.json").exists()
    ]
    if not candidates:
        raise FileNotFoundError(f"No ablation summaries found under {root}")
    return sorted(candidates)[-1]


def value(parsed_summary: dict[str, Any], key: str) -> str:
    return str(parsed_summary.get(key, "-"))


def build_ablation_table(summary: dict[str, Any]) -> str:
    headers = ["Variant", *[label for _, label in TABLE_COLUMNS]]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for experiment in summary.get("experiments", []):
        if experiment.get("name") == "safety_stress_cases":
            continue
        parsed = experiment.get("parsed_summary") or {}
        row = [
            experiment.get("name", "-"),
            *[value(parsed, key) for key, _ in TABLE_COLUMNS],
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def build_safety_table(summary: dict[str, Any]) -> str:
    headers = ["Experiment", "Return Code", "Success", "Safety Cases Passed"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    safety_records = [
        experiment
        for experiment in summary.get("experiments", [])
        if experiment.get("name") == "safety_stress_cases"
    ]
    if not safety_records:
        lines.append("| safety_stress_cases | - | not run | - |")
        return "\n".join(lines) + "\n"

    for experiment in safety_records:
        parsed = experiment.get("parsed_summary") or {}
        row = [
            experiment.get("name", "-"),
            str(experiment.get("return_code", "-")),
            str(experiment.get("success", "-")),
            value(parsed, "safety_case_pass_count"),
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def write_report_asset(filename: str, content: str) -> Path:
    output_dir = PROJECT_ROOT / "report_assets" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export ablation tables as markdown.")
    parser.add_argument("--input", help="Path to ablation_summary.json.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use latest outputs/ablations/<timestamp>/ablation_summary.json.",
    )
    parser.add_argument("--ablations-root", default="outputs/ablations")
    args = parser.parse_args()

    if args.latest:
        ablation_dir = find_latest_ablation_dir(PROJECT_ROOT / args.ablations_root)
        summary_path = ablation_dir / "ablation_summary.json"
    elif args.input:
        summary_path = Path(args.input)
        if not summary_path.is_absolute():
            summary_path = PROJECT_ROOT / summary_path
        ablation_dir = summary_path.parent
    else:
        parser.error("Use --latest or --input <ablation_summary.json>.")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    ablation_table = build_ablation_table(summary)
    safety_table = build_safety_table(summary)

    ablation_path = ablation_dir / "ablation_table.md"
    safety_path = ablation_dir / "safety_table.md"
    ablation_path.write_text(ablation_table, encoding="utf-8")
    safety_path.write_text(safety_table, encoding="utf-8")

    report_ablation_path = write_report_asset("ablation_table.md", ablation_table)
    report_safety_path = write_report_asset("safety_table.md", safety_table)

    print(f"ablation_table_path: {ablation_path}")
    print(f"safety_table_path: {safety_path}")
    print(f"report_ablation_table_path: {report_ablation_path}")
    print(f"report_safety_table_path: {report_safety_path}")


if __name__ == "__main__":
    main()
