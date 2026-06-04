#!/usr/bin/env python3
"""Run an offline failure-memory retrieval demo."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.llm.memory_prompt_builder import build_memory_augmented_patch_prompt
from scicodepilot.memory.record import FailureMemoryRecord
from scicodepilot.memory.store import FailureMemoryStore


DEFAULT_MEMORY_PATH = PROJECT_ROOT / "artifacts" / "failure_memory" / "memory_records.jsonl"


def ensure_memory_records(memory_path: Path) -> None:
    if memory_path.exists():
        return
    subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "export_failure_memory_records.py"),
            "--latest",
            "--output",
            str(memory_path),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )


def build_query() -> FailureMemoryRecord:
    return FailureMemoryRecord(
        record_id="demo_query_tensor_shape",
        task_id="external_demo_query",
        error_type="tensor_shape",
        failure_category="source_code",
        command="python train.py",
        exception_type="RuntimeError",
        error_message="mat1 and mat2 shapes cannot be multiplied",
        traceback_summary="RuntimeError from matrix multiplication with incompatible tensor dimensions.",
        root_cause_hypothesis="The downstream layer input dimension does not match upstream tensor features.",
        repair_action="Inspect tensor dimensions and align the downstream layer input dimension.",
        patch_plan_summary=None,
        verification_success=None,
        score=None,
        created_from="memory_retrieval_demo",
        metadata={"scope": "offline demo query"},
    )


def main() -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / "outputs" / "memory_retrieval" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    ensure_memory_records(DEFAULT_MEMORY_PATH)
    store = FailureMemoryStore.load_jsonl(DEFAULT_MEMORY_PATH)
    query = build_query()
    retrieved = store.retrieve(query, top_k=3)
    prompt = build_memory_augmented_patch_prompt(query, retrieved)

    summary = {
        "memory_path": str(DEFAULT_MEMORY_PATH),
        "output_dir": str(output_dir),
        "query": query.to_dict(),
        "retrieved": [
            {
                "record": item.record.to_dict(),
                "score": item.score,
                "matched_terms": item.matched_terms,
            }
            for item in retrieved
        ],
        "scope_note": "Offline memory retrieval demo; no real LLM call and no public benchmark claim.",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    lines = [
        "# Memory Retrieval Demo Summary",
        "",
        f"- Memory path: `{DEFAULT_MEMORY_PATH}`",
        "- Query failure: `tensor_shape`",
        f"- Retrieved count: {len(retrieved)}",
        "- Scope: offline demo only; no real LLM call.",
        "",
        "| Rank | Record ID | Error Type | Score | Matched Terms |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for rank, item in enumerate(retrieved, start=1):
        lines.append(
            "| "
            f"{rank} | {item.record.record_id} | {item.record.error_type} | "
            f"{item.score} | {', '.join(item.matched_terms[:8]) or '-'} |"
        )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"memory_retrieval_output: {output_dir}")
    if retrieved:
        print(
            "top_memory: "
            f"{retrieved[0].record.record_id} "
            f"score={retrieved[0].score}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
