from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scicodepilot.memory.record import FailureMemoryRecord
from scicodepilot.memory.store import FailureMemoryStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def make_record(
    record_id: str,
    error_type: str,
    category: str,
    message: str,
) -> FailureMemoryRecord:
    return FailureMemoryRecord(
        record_id=record_id,
        task_id=record_id.replace("record", "task"),
        error_type=error_type,
        failure_category=category,
        command="python train.py",
        exception_type="RuntimeError",
        error_message=message,
        traceback_summary=message,
        root_cause_hypothesis=message,
        repair_action=message,
        patch_plan_summary=message,
        verification_success=True,
        score=1.0,
        created_from="test",
        metadata={},
    )


def run_eval(
    memory_path: Path,
    output_dir: Path,
    table_output: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "evaluate_memory_retrieval.py"),
            "--memory-path",
            str(memory_path),
            "--output-dir",
            str(output_dir),
            "--table-output",
            str(table_output),
            "--top-k",
            "3",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_memory_retrieval_eval_writes_summary_and_table(tmp_path) -> None:
    memory_path = tmp_path / "memory.jsonl"
    output_dir = tmp_path / "eval_output"
    table_output = tmp_path / "memory_retrieval_eval.md"
    FailureMemoryStore(
        [
            make_record(
                "record_tensor",
                "tensor_shape",
                "source_code",
                "mat1 and mat2 shapes cannot be multiplied",
            ),
            make_record(
                "record_missing_module",
                "missing_module",
                "env_data",
                "No module named sklearn_extra",
            ),
            make_record(
                "record_dtype",
                "dtype_mismatch",
                "source_code",
                "float64 dtype mismatch",
            ),
        ]
    ).save_jsonl(memory_path)

    result = run_eval(memory_path, output_dir, table_output)

    assert result.returncode == 0
    assert (output_dir / "summary.md").exists()
    assert (output_dir / "summary.json").exists()
    assert table_output.exists()
    assert "memory_retrieval_eval_output" in result.stdout
    assert "memory_retrieval_eval_table" in result.stdout

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert "metrics" in summary
    assert summary["metrics"]["total_queries"] == 3
    assert "top1_self_match_count" in summary["metrics"]
    assert "claim_scope" in summary

    table_text = table_output.read_text(encoding="utf-8")
    assert "Memory Retrieval Evaluation" in table_text
    assert "internal controlled benchmark only" in table_text
    assert "Top-1 retrieved memory" in table_text


def test_memory_retrieval_eval_empty_memory_file_writes_zero_query_summary(tmp_path) -> None:
    memory_path = tmp_path / "empty.jsonl"
    output_dir = tmp_path / "empty_eval"
    table_output = tmp_path / "empty_table.md"
    memory_path.write_text("", encoding="utf-8")

    result = run_eval(memory_path, output_dir, table_output)

    assert result.returncode == 0
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["record_count"] == 0
    assert summary["metrics"]["total_queries"] == 0
    assert (output_dir / "summary.md").exists()
    assert table_output.exists()


def test_memory_retrieval_eval_malformed_jsonl_surfaces_line_number(tmp_path) -> None:
    memory_path = tmp_path / "bad.jsonl"
    output_dir = tmp_path / "bad_eval"
    table_output = tmp_path / "bad_table.md"
    memory_path.write_text("{bad json}\n", encoding="utf-8")

    result = run_eval(memory_path, output_dir, table_output)

    assert result.returncode != 0
    assert "line 1" in result.stderr


def test_memory_retrieval_eval_generated_files_avoid_public_benchmark_claims(tmp_path) -> None:
    memory_path = tmp_path / "memory.jsonl"
    output_dir = tmp_path / "eval_output"
    table_output = tmp_path / "memory_retrieval_eval.md"
    FailureMemoryStore(
        [
            make_record(
                "record_tensor",
                "tensor_shape",
                "source_code",
                "mat1 and mat2 shapes cannot be multiplied",
            )
        ]
    ).save_jsonl(memory_path)

    result = run_eval(memory_path, output_dir, table_output)

    assert result.returncode == 0
    generated = "\n".join(
        [
            (output_dir / "summary.md").read_text(encoding="utf-8"),
            (output_dir / "summary.json").read_text(encoding="utf-8"),
            table_output.read_text(encoding="utf-8"),
        ]
    )
    for forbidden in [
        "SOTA",
        "outperforms",
        "completed SWE-bench",
        "completed BugsInPy",
    ]:
        assert forbidden not in generated
