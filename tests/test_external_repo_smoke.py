from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def snapshot_repo(repo_dir: Path) -> dict[str, str]:
    return {
        str(path.relative_to(repo_dir)): path.read_text(encoding="utf-8")
        for path in sorted(repo_dir.rglob("*"))
        if path.is_file()
    }


def make_external_repo(tmp_path: Path) -> Path:
    repo_dir = tmp_path / "external_repo"
    repo_dir.mkdir()
    (repo_dir / "fail.py").write_text(
        "import definitely_missing_external_smoke_dependency\n",
        encoding="utf-8",
    )
    (repo_dir / "README.md").write_text("temporary external repo\n", encoding="utf-8")
    return repo_dir


def run_smoke(repo_dir: Path, output_dir: Path, mode: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_external_repo_smoke.py"),
            "--repo-path",
            str(repo_dir),
            "--command",
            f"{sys.executable} fail.py",
            "--mode",
            mode,
            "--output-dir",
            str(output_dir),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_external_repo_smoke_diagnosis_writes_summaries_without_mutating_repo(tmp_path) -> None:
    repo_dir = make_external_repo(tmp_path)
    before = snapshot_repo(repo_dir)
    output_dir = tmp_path / "smoke_diagnosis"

    result = run_smoke(repo_dir, output_dir, "diagnosis")

    assert result.returncode == 0
    assert (output_dir / "summary.md").exists()
    assert (output_dir / "summary.json").exists()
    assert snapshot_repo(repo_dir) == before

    summary_text = (output_dir / "summary.md").read_text(encoding="utf-8")
    summary_json = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert "FailureMemory" in summary_text or "unsupported_external_failure" in summary_text
    assert summary_json["parsed_error"]["error_type"] == "missing_module"
    assert summary_json["original_repo_mutated"] is False


def test_external_repo_smoke_repair_plan_does_not_apply_patch_to_original_repo(tmp_path) -> None:
    repo_dir = make_external_repo(tmp_path)
    before = snapshot_repo(repo_dir)
    output_dir = tmp_path / "smoke_repair_plan"

    result = run_smoke(repo_dir, output_dir, "repair-plan")

    assert result.returncode == 0
    assert snapshot_repo(repo_dir) == before

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["repair_plan"]["plan_type"] == "EnvRepairPlan"
    assert "workspace" in summary["workspace_dir"]
    assert Path(summary["workspace_dir"]).exists()
