from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scicodepilot.memory.store import FailureMemoryStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_export_failure_memory_records_writes_jsonl(tmp_path) -> None:
    summary_path = tmp_path / "ablation_summary.json"
    output_path = tmp_path / "memory_records.jsonl"
    summary = {
        "experiments": [
            {
                "name": "full_rule_based_repair",
                "parsed_summary": {
                    "patch_applied_count": 8,
                    "verification_success_count": 8,
                    "env_repair_plan_count": 2,
                },
            }
        ]
    }
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "export_failure_memory_records.py"),
            "--input",
            str(summary_path),
            "--output",
            str(output_path),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_path.exists()
    assert "failure_memory_records_path" in result.stdout

    records = FailureMemoryStore.load_jsonl(output_path).all_records()
    assert records
    assert any(record.error_type == "tensor_shape" for record in records)
    assert any(record.error_type == "missing_module" for record in records)
