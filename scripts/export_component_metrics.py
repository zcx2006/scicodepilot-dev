#!/usr/bin/env python3
"""Export component metrics from ablation summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ABLATIONS_ROOT = PROJECT_ROOT / "outputs" / "ablations"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "report_assets" / "tables" / "component_metrics.md"

METRIC_LABELS = (
    ("total_tasks", "total controlled tasks"),
    ("diagnosis_pass_count", "diagnosis pass count"),
    ("patch_plan_count", "patch plan count"),
    ("env_repair_plan_count", "env repair plan count"),
    ("patch_review_count", "patch review count"),
    ("patch_applied_count", "patch applied count"),
    ("verification_success_count", "verification success count"),
    ("scored_task_count", "scored task count"),
    ("average_score", "average score"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export internal component metrics.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Read the latest outputs/ablations/*/ablation_summary.json. Default behavior.",
    )
    parser.add_argument("--input", help="Explicit ablation_summary.json path.")
    parser.add_argument("--ablations-root", default=str(DEFAULT_ABLATIONS_ROOT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    return parser.parse_args()


def find_latest_summary(ablations_root: Path) -> Path | None:
    if not ablations_root.exists():
        return None
    candidates = sorted(ablations_root.glob("*/ablation_summary.json"))
    if not candidates:
        return None
    return candidates[-1]


def load_summary(args: argparse.Namespace) -> tuple[dict[str, Any] | None, Path | None]:
    if args.input:
        summary_path = Path(args.input)
        if not summary_path.is_absolute():
            summary_path = PROJECT_ROOT / summary_path
    else:
        root = Path(args.ablations_root)
        if not root.is_absolute():
            root = PROJECT_ROOT / root
        summary_path = find_latest_summary(root)

    if summary_path is None or not summary_path.exists():
        return None, summary_path
    return json.loads(summary_path.read_text(encoding="utf-8")), summary_path


# def choose_main_metrics(summary: dict[str, Any]) -> dict[str, Any]:
#     experiments = summary.get("experiments", [])
#     preferred_names = ("full_rule_based_repair", "diagnosis_only", "repair_without_apply")
#     for name in preferred_names:
#         for experiment in experiments:
#             if experiment.get("name") == name:
#                 return experiment.get("parsed_summary") or {}
#     for experiment in experiments:
#         parsed = experiment.get("parsed_summary") or {}
#         if parsed:
#             return parsed
#     return {}

def choose_main_experiment(summary: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    experiments = summary.get("experiments", [])
    preferred_names = ("full_rule_based_repair", "repair_without_apply", "diagnosis_only")
    for name in preferred_names:
        for experiment in experiments:
            if experiment.get("name") == name:
                return name, experiment.get("parsed_summary") or {}
    for experiment in experiments:
        parsed = experiment.get("parsed_summary") or {}
        if parsed:
            return experiment.get("name"), parsed
    return None, {}


def find_experiment_metrics(summary: dict[str, Any], name: str) -> dict[str, Any]:
    for experiment in summary.get("experiments", []):
        if experiment.get("name") == name:
            return experiment.get("parsed_summary") or {}
    return {}


def safety_pass_count(summary: dict[str, Any]) -> Any:
    for experiment in summary.get("experiments", []):
        if experiment.get("name") != "safety_stress_cases":
            continue
        parsed = experiment.get("parsed_summary") or {}
        return parsed.get("safety_case_pass_count", "-")
    return "-"


def build_table(summary: dict[str, Any] | None, summary_path: Path | None) -> str:
    lines = [
        "# Component Metrics",
        "",
        "These component metrics are for internal controlled benchmark only.",
        "",
    ]

    if summary is None:
        lines.extend(
            [
                "No ablation_summary.json was found.",
                "",
                f"- Searched path: `{summary_path}`",
            ]
        )
        return "\n".join(lines) + "\n"

    main_experiment_name, metrics = choose_main_experiment(summary)
    diagnosis_metrics = find_experiment_metrics(summary, "diagnosis_only")

    lines.extend(
        [
            f"- Source summary: `{summary_path}`",
            f"- Main variant: `{main_experiment_name}`",
            "- Diagnosis metric policy: use `diagnosis_only` when available; otherwise mark as not recorded.",
            "",
            "| Metric | Value |",
            "| --- | --- |",
        ]
    )

    for key, label in METRIC_LABELS:
        if key == "diagnosis_pass_count":
            diagnosis_value = diagnosis_metrics.get("diagnosis_pass_count")
            diagnosis_total = diagnosis_metrics.get("total_tasks")

            if diagnosis_value is not None and diagnosis_total is not None:
                value = f"{diagnosis_value}/{diagnosis_total}"
            elif diagnosis_value is not None:
                value = diagnosis_value
            else:
                value = "not recorded in this variant"
        else:
            value = metrics.get(key, "-")

        lines.append(f"| {label} | {value} |")

    lines.append(f"| safety stress case pass count | {safety_pass_count(summary)} |")
    return "\n".join(lines) + "\n"


def export_metrics(args: argparse.Namespace) -> Path:
    summary, summary_path = load_summary(args)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_table(summary, summary_path), encoding="utf-8")
    return output_path


def main() -> int:
    args = parse_args()
    output_path = export_metrics(args)
    print(f"component_metrics_path: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
