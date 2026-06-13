from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_memory_retrieval_demo_creates_artifacts() -> None:
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "run_memory_retrieval_demo.py")],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    match = re.search(r"memory_retrieval_output: (.+)", result.stdout)
    assert match

    output_dir = Path(match.group(1).strip())
    summary_md = output_dir / "summary.md"
    summary_json = output_dir / "summary.json"
    prompt_md = output_dir / "prompt.md"

    assert summary_md.exists()
    assert summary_json.exists()
    assert prompt_md.exists()
    assert "tensor_shape" in summary_md.read_text(encoding="utf-8")
    assert "Return only structured PatchPlan JSON" in prompt_md.read_text(
        encoding="utf-8"
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["retrieved"]
