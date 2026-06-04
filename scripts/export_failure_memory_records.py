#!/usr/bin/env python3
"""Export conservative failure memory records for internal controlled tasks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.memory.failure_memory import FailureMemoryBuilder
from scicodepilot.memory.record import FailureMemoryRecord
from scicodepilot.memory.store import FailureMemoryStore
from scicodepilot.tools.traceback_parser import ParsedError


DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "failure_memory" / "memory_records.jsonl"
DEFAULT_ABLATIONS_ROOT = PROJECT_ROOT / "outputs" / "ablations"

TASK_FAILURES: dict[str, dict[str, Any]] = {
    "repair_tensor_shape_001": {
        "error_type": "tensor_shape",
        "failure_category": "source_code",
        "exception_type": "RuntimeError",
        "error_message": "mat1 and mat2 shapes cannot be multiplied",
        "patch_plan_summary": "Align classifier_expected_dim with upstream_feature_dim.",
    },
    "repair_dtype_mismatch_002": {
        "error_type": "dtype_mismatch",
        "failure_category": "source_code",
        "exception_type": "RuntimeError",
        "error_message": "mat1 and mat2 must have the same dtype",
        "patch_plan_summary": "Convert float64 tensor construction to float32.",
    },
    "repair_missing_module_003": {
        "error_type": "missing_module",
        "failure_category": "env_data",
        "exception_type": "ModuleNotFoundError",
        "error_message": "No module named definitely_missing_scicodepilot_dependency",
        "patch_plan_summary": "Create EnvRepairPlan for missing dependency; do not install automatically.",
    },
    "repair_missing_file_004": {
        "error_type": "missing_file",
        "failure_category": "env_data",
        "exception_type": "FileNotFoundError",
        "error_message": "No such file or directory",
        "patch_plan_summary": "Create EnvRepairPlan for missing data/config file; do not create fake data.",
    },
    "repair_entrypoint_error_005": {
        "error_type": "entrypoint_error",
        "failure_category": "source_code",
        "exception_type": "NameError",
        "error_message": "NameError: name 'mainn'",
        "patch_plan_summary": "Replace misspelled mainn entrypoint with main.",
    },
    "repair_label_shape_006": {
        "error_type": "label_shape",
        "failure_category": "source_code",
        "exception_type": "ValueError",
        "error_message": "Expected input batch_size to match target batch_size",
        "patch_plan_summary": "Align label batch size with logits batch size.",
    },
    "repair_device_mismatch_007": {
        "error_type": "device_mismatch",
        "failure_category": "source_code",
        "exception_type": "RuntimeError",
        "error_message": "Expected all tensors to be on the same device",
        "patch_plan_summary": "Align input tensor device with model device.",
    },
    "repair_loss_input_008": {
        "error_type": "loss_input_error",
        "failure_category": "source_code",
        "exception_type": "RuntimeError",
        "error_message": "CrossEntropyLoss expected class index targets",
        "patch_plan_summary": "Use class-index targets for CrossEntropyLoss.",
    },
    "repair_collate_fn_009": {
        "error_type": "collate_fn_error",
        "failure_category": "source_code",
        "exception_type": "KeyError",
        "error_message": "batch missing expected key",
        "patch_plan_summary": "Return x and y keys from collate_fn.",
    },
    "repair_config_key_010": {
        "error_type": "config_key_error",
        "failure_category": "source_code",
        "exception_type": "KeyError",
        "error_message": "missing experiment config key learningrate",
        "patch_plan_summary": "Use learning_rate config key.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export failure memory records.")
    parser.add_argument("--latest", action="store_true", help="Use latest ablation summary.")
    parser.add_argument("--input", help="Explicit ablation_summary.json path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--ablations-root", default=str(DEFAULT_ABLATIONS_ROOT))
    return parser.parse_args()


def latest_summary(root: Path) -> Path | None:
    if not root.exists():
        return None
    candidates = sorted(root.glob("*/ablation_summary.json"))
    return candidates[-1] if candidates else None


def load_summary(args: argparse.Namespace) -> tuple[dict[str, Any] | None, Path | None]:
    if args.input:
        summary_path = Path(args.input)
        if not summary_path.is_absolute():
            summary_path = PROJECT_ROOT / summary_path
    else:
        root = Path(args.ablations_root)
        if not root.is_absolute():
            root = PROJECT_ROOT / root
        summary_path = latest_summary(root)

    if summary_path is None or not summary_path.exists():
        return None, summary_path
    return json.loads(summary_path.read_text(encoding="utf-8")), summary_path


def full_repair_metrics(summary: dict[str, Any] | None) -> dict[str, Any]:
    if summary is None:
        return {}
    for experiment in summary.get("experiments", []):
        if experiment.get("name") == "full_rule_based_repair":
            return experiment.get("parsed_summary") or {}
    return {}


def read_task_metadata(task_id: str) -> dict[str, Any]:
    metadata_path = PROJECT_ROOT / "benchmark" / "tasks" / task_id / "metadata.json"
    if not metadata_path.exists():
        return {}
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def build_records(
    summary: dict[str, Any] | None,
    summary_path: Path | None,
) -> list[FailureMemoryRecord]:
    metrics = full_repair_metrics(summary)
    records: list[FailureMemoryRecord] = []
    builder = FailureMemoryBuilder()

    for task_id, failure in sorted(TASK_FAILURES.items()):
        metadata = read_task_metadata(task_id)
        parsed = ParsedError(
            error_type=failure["error_type"],
            summary=failure["error_message"],
            evidence=[failure["error_message"]],
        )
        memory = builder.from_parsed_error(parsed)
        source_task_success = (
            failure["failure_category"] == "source_code"
            and metrics.get("patch_applied_count", 0) >= 8
            and metrics.get("verification_success_count", 0) >= 8
        )
        env_task_success = (
            failure["failure_category"] == "env_data"
            and metrics.get("env_repair_plan_count", 0) >= 2
        )
        verification_success = source_task_success or env_task_success
        score = 1.0 if source_task_success else None
        records.append(
            FailureMemoryRecord(
                record_id=f"internal_controlled_{task_id}",
                task_id=task_id,
                error_type=failure["error_type"],
                failure_category=failure["failure_category"],
                command=metadata.get("entry_command"),
                exception_type=failure["exception_type"],
                error_message=failure["error_message"],
                traceback_summary=parsed.summary,
                root_cause_hypothesis=memory.root_cause_hypothesis,
                repair_action=memory.repair_action,
                patch_plan_summary=failure["patch_plan_summary"],
                verification_success=verification_success,
                score=score,
                created_from="internal_controlled_benchmark",
                metadata={
                    "task_name": metadata.get("task_name"),
                    "category": metadata.get("category"),
                    "source_summary": str(summary_path) if summary_path else None,
                    "record_scope": "internal controlled benchmark only",
                },
            )
        )
    return records


def main() -> int:
    args = parse_args()
    summary, summary_path = load_summary(args)
    records = build_records(summary, summary_path)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    store = FailureMemoryStore(records)
    store.save_jsonl(output_path)
    print(f"failure_memory_records_path: {output_path}")
    print(f"record_count: {len(records)}")
    if not records:
        print("warning: no records could be extracted; wrote an empty JSONL file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
