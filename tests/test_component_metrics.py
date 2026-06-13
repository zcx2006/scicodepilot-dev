from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_export_component_metrics_from_explicit_summary(tmp_path) -> None:
    summary_path = tmp_path / "ablation_summary.json"
    output_path = tmp_path / "component_metrics.md"
    summary = {
        "experiments": [
            {
                "name": "full_rule_based_repair",
                "parsed_summary": {
                    "total_tasks": 10,
                    "diagnosis_pass_count": 10,
                    "patch_plan_count": 8,
                    "env_repair_plan_count": 2,
                    "patch_review_count": 8,
                    "patch_applied_count": 8,
                    "verification_success_count": 8,
                    "scored_task_count": 10,
                    "average_score": 1.0,
                },
            },
            {
                "name": "safety_stress_cases",
                "parsed_summary": {
                    "safety_case_pass_count": 10,
                },
            },
        ]
    }
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "export_component_metrics.py"),
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

    text = output_path.read_text(encoding="utf-8")
    assert "component metrics are for internal controlled benchmark only" in text
    assert "diagnosis pass count" in text
    assert "patch applied count" in text
    assert "env repair plan count" in text
