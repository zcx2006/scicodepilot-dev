#!/usr/bin/env python3
"""Evaluate deterministic failure-memory retrieval on internal records."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.memory.record import FailureMemoryRecord, RetrievedFailureMemory
from scicodepilot.memory.store import FailureMemoryStore


DEFAULT_MEMORY_PATH = PROJECT_ROOT / "artifacts" / "failure_memory" / "memory_records.jsonl"
DEFAULT_TABLE_OUTPUT = PROJECT_ROOT / "report_assets" / "tables" / "memory_retrieval_eval.md"
CLAIM_SCOPE = (
    "internal controlled benchmark only; component-level retrieval sanity evaluation; "
    "not public benchmark; not real LLM evaluation; not external baseline comparison"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate deterministic FailureMemory retrieval."
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use artifacts/failure_memory/memory_records.jsonl. Default behavior.",
    )
    parser.add_argument("--memory-path", default=str(DEFAULT_MEMORY_PATH))
    parser.add_argument("--output-dir")
    parser.add_argument("--table-output", default=str(DEFAULT_TABLE_OUTPUT))
    parser.add_argument("--top-k", type=int, default=3)
    return parser.parse_args()


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        return PROJECT_ROOT / path
    return path


def default_output_dir() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return PROJECT_ROOT / "outputs" / "memory_retrieval_eval" / timestamp


def retrieval_row(
    query: FailureMemoryRecord,
    retrieved: list[RetrievedFailureMemory],
) -> dict[str, Any]:
    return {
        "query_record_id": query.record_id,
        "query_task_id": query.task_id,
        "query_error_type": query.error_type,
        "query_failure_category": query.failure_category,
        "top_results": [
            {
                "record_id": item.record.record_id,
                "task_id": item.record.task_id,
                "error_type": item.record.error_type,
                "failure_category": item.record.failure_category,
                "score": item.score,
                "matched_terms": item.matched_terms,
            }
            for item in retrieved
        ],
    }


def compute_metrics(
    records: list[FailureMemoryRecord],
    rows: list[dict[str, Any]],
    top_k: int,
) -> dict[str, Any]:
    top1_scores: list[float] = []
    top_scores: list[float] = []
    metrics = {
        "total_queries": len(records),
        "top1_self_match_count": 0,
        "top3_self_match_count": 0,
        "top1_error_type_match_count": 0,
        "top3_error_type_match_count": 0,
        "top1_failure_category_match_count": 0,
        "top3_failure_category_match_count": 0,
        "source_repair_query_count": 0,
        "env_or_data_query_count": 0,
        "average_top1_score": 0.0,
        "average_top3_score": 0.0,
        "empty_result_count": 0,
    }

    for query, row in zip(records, rows):
        top_results = row["top_results"]
        if not top_results:
            metrics["empty_result_count"] += 1
            continue

        if query.failure_category == "source_code":
            metrics["source_repair_query_count"] += 1
        elif query.failure_category == "env_data":
            metrics["env_or_data_query_count"] += 1

        top1 = top_results[0]
        top1_scores.append(float(top1["score"]))
        top_scores.extend(float(item["score"]) for item in top_results[:top_k])

        if top1["record_id"] == query.record_id:
            metrics["top1_self_match_count"] += 1
        if any(item["record_id"] == query.record_id for item in top_results[:top_k]):
            metrics["top3_self_match_count"] += 1
        if top1["error_type"] == query.error_type:
            metrics["top1_error_type_match_count"] += 1
        if any(item["error_type"] == query.error_type for item in top_results[:top_k]):
            metrics["top3_error_type_match_count"] += 1
        if top1["failure_category"] == query.failure_category:
            metrics["top1_failure_category_match_count"] += 1
        if any(
            item["failure_category"] == query.failure_category
            for item in top_results[:top_k]
        ):
            metrics["top3_failure_category_match_count"] += 1

    if top1_scores:
        metrics["average_top1_score"] = round(sum(top1_scores) / len(top1_scores), 6)
    if top_scores:
        metrics["average_top3_score"] = round(sum(top_scores) / len(top_scores), 6)
    return metrics


def evaluate(memory_path: Path, top_k: int) -> dict[str, Any]:
    store = FailureMemoryStore.load_jsonl(memory_path)
    records = store.all_records()
    rows = [retrieval_row(record, store.retrieve(record, top_k=top_k)) for record in records]
    metrics = compute_metrics(records, rows, top_k=top_k)
    return {
        "memory_path": str(memory_path),
        "record_count": len(records),
        "top_k": top_k,
        "metrics": metrics,
        "rows": rows,
        "claim_scope": CLAIM_SCOPE,
        "notes": [
            "Self-match metrics are useful because current internal controlled records have one record per error type.",
            "Same-error retrieval beyond self-match is limited by the current one-record-per-error-type data.",
        ],
    }


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def build_table(summary: dict[str, Any]) -> str:
    lines = [
        "# Memory Retrieval Evaluation",
        "",
        (
            "These component metrics are for internal controlled benchmark only. "
            "They do not claim public benchmark performance, real LLM performance, "
            "external baseline comparison, or real-world generalization."
        ),
        "",
        "| Query task | Query error type | Query category | Top-1 retrieved memory | Top-1 score | Top-1 error type match | Top-3 contains same error type |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in summary["rows"]:
        top_results = row["top_results"]
        top1 = top_results[0] if top_results else {}
        top1_error_match = bool(top1) and top1.get("error_type") == row["query_error_type"]
        top3_error_match = any(
            item.get("error_type") == row["query_error_type"]
            for item in top_results[: summary["top_k"]]
        )
        lines.append(
            "| "
            f"{row['query_task_id']} | "
            f"{row['query_error_type']} | "
            f"{row['query_failure_category']} | "
            f"{top1.get('record_id', '-')} | "
            f"{top1.get('score', '-')} | "
            f"{yes_no(top1_error_match)} | "
            f"{yes_no(top3_error_match)} |"
        )
    if not summary["rows"]:
        lines.append("| - | - | - | - | - | no | no |")
    return "\n".join(lines) + "\n"


def build_summary_markdown(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    lines = [
        "# Memory Retrieval Evaluation Summary",
        "",
        f"- Memory path: `{summary['memory_path']}`",
        f"- Record count: {summary['record_count']}",
        f"- Top-k: {summary['top_k']}",
        f"- Claim scope: {summary['claim_scope']}",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Compact Results",
            "",
            "| Query record | Query error type | Top-1 memory | Top-1 score |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in summary["rows"]:
        top1 = row["top_results"][0] if row["top_results"] else {}
        lines.append(
            "| "
            f"{row['query_record_id']} | "
            f"{row['query_error_type']} | "
            f"{top1.get('record_id', '-')} | "
            f"{top1.get('score', '-')} |"
        )
    if not summary["rows"]:
        lines.append("| - | - | - | - |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- not public benchmark",
            "- not real LLM evaluation",
            "- not external baseline comparison",
            "- not a generalization claim",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(summary: dict[str, Any], output_dir: Path, table_path: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "summary.md").write_text(
        build_summary_markdown(summary),
        encoding="utf-8",
    )
    table_path.write_text(build_table(summary), encoding="utf-8")


def main() -> int:
    args = parse_args()
    memory_path = resolve_project_path(args.memory_path)
    output_dir = resolve_project_path(args.output_dir) if args.output_dir else default_output_dir()
    table_path = resolve_project_path(args.table_output)

    if args.top_k < 1:
        print("top-k must be >= 1", file=sys.stderr)
        return 2

    try:
        summary = evaluate(memory_path, top_k=args.top_k)
    except ValueError as exc:
        print(f"memory retrieval evaluation failed: {exc}", file=sys.stderr)
        return 1

    write_outputs(summary, output_dir, table_path)
    print(f"memory_retrieval_eval_output: {output_dir}")
    print(f"memory_retrieval_eval_table: {table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
