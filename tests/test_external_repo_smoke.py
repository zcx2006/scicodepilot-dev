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


def test_external_repo_smoke_repair_succeeds_on_minimal_assertion_case(tmp_path) -> None:
    repo_dir = tmp_path / "external_assertion_repo"
    repo_dir.mkdir()
    sample_path = repo_dir / "sample.py"
    original_text = (
        "def cli_bool_option(params, command_option, param):\n"
        "    param = params.get(param)\n"
        "    assert isinstance(param, bool)\n"
        "    return [command_option] if param else []\n"
    )
    sample_path.write_text(original_text, encoding="utf-8")
    output_dir = tmp_path / "smoke_repair"

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_external_repo_smoke.py"),
            "--repo-path",
            str(repo_dir),
            "--command",
            (
                f"{sys.executable} -c \"from sample import cli_bool_option; "
                "print(cli_bool_option({}, '--flag', 'missing'))\""
            ),
            "--mode",
            "repair",
            "--confirm-apply",
            "--output-dir",
            str(output_dir),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert sample_path.read_text(encoding="utf-8") == original_text

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["before_return_code"] == 1
    assert summary["after_return_code"] == 0
    assert summary["detected_failure_type"] == "external_assertion_failure"
    assert summary["failure_memory_specialized"] is True
    assert summary["patch_plan_generated"] is True
    assert summary["patch_applied"] is True
    assert summary["original_repo_mutated"] is False
    assert summary["final_status"] == "patch_success"
    assert "if param is None:" in summary["patch_diff"]


def test_external_repo_smoke_repair_succeeds_on_minimal_type_error_case(tmp_path) -> None:
    repo_dir = tmp_path / "external_type_error_repo"
    repo_dir.mkdir()
    sample_path = repo_dir / "sample.py"
    original_text = (
        "import re\n"
        "compat_str = str\n"
        "\n"
        "def str_to_int(int_str):\n"
        "    if int_str is None:\n"
        "        return None\n"
        "    int_str = re.sub(r'[,\\\\.]', '', int_str)\n"
        "    return int(int_str)\n"
    )
    sample_path.write_text(original_text, encoding="utf-8")
    output_dir = tmp_path / "smoke_type_repair"

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_external_repo_smoke.py"),
            "--repo-path",
            str(repo_dir),
            "--command",
            f"{sys.executable} -c \"from sample import str_to_int; print(str_to_int(123))\"",
            "--mode",
            "repair",
            "--confirm-apply",
            "--output-dir",
            str(output_dir),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert sample_path.read_text(encoding="utf-8") == original_text

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["before_return_code"] == 1
    assert summary["after_return_code"] == 0
    assert summary["detected_failure_type"] == "external_type_error"
    assert summary["patch_plan_generated"] is True
    assert summary["patch_applied"] is True
    assert summary["original_repo_mutated"] is False
    assert summary["final_status"] == "patch_success"
    assert "if not isinstance(int_str, compat_str):" in summary["patch_diff"]
    workspace_sample = Path(summary["workspace_path"]) / "sample.py"
    assert "if not isinstance(int_str, compat_str):" in workspace_sample.read_text(
        encoding="utf-8"
    )


def test_external_repo_smoke_repair_succeeds_on_minimal_unified_strdate_case(tmp_path) -> None:
    repo_dir = tmp_path / "external_unified_strdate_repo"
    repo_dir.mkdir()
    sample_path = repo_dir / "sample.py"
    original_text = (
        "def compat_str(x):\n"
        "    return str(x)\n"
        "\n"
        "def unified_strdate(date_str):\n"
        "    upload_date = None\n"
        "    return compat_str(upload_date)\n"
    )
    sample_path.write_text(original_text, encoding="utf-8")
    output_dir = tmp_path / "smoke_unified_repair"

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_external_repo_smoke.py"),
            "--repo-path",
            str(repo_dir),
            "--command",
            (
                f"{sys.executable} -c \"from sample import unified_strdate; "
                "assert unified_strdate('not-a-date') is None\""
            ),
            "--mode",
            "repair",
            "--confirm-apply",
            "--output-dir",
            str(output_dir),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert sample_path.read_text(encoding="utf-8") == original_text

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["before_return_code"] == 1
    assert summary["after_return_code"] == 0
    assert summary["detected_failure_type"] == "external_assertion_failure"
    assert summary["parsed_error"]["assertion_location"] == "command"
    assert summary["parsed_error"]["target_symbol"] == "unified_strdate"
    assert summary["patch_plan_generated"] is True
    assert summary["patch_applied"] is True
    assert summary["original_repo_mutated"] is False
    assert summary["final_status"] == "patch_success"
    assert "if upload_date is not None:" in summary["patch_diff"]
    workspace_sample = Path(summary["workspace_path"]) / "sample.py"
    assert "if upload_date is not None:" in workspace_sample.read_text(
        encoding="utf-8"
    )


def test_external_repo_smoke_classifies_pipes_env_failure(tmp_path) -> None:
    repo_dir = tmp_path / "external_env_repo"
    repo_dir.mkdir()
    (repo_dir / "fail.py").write_text(
        "raise ModuleNotFoundError(\"No module named 'pipes'\")\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "smoke_env"

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_external_repo_smoke.py"),
            "--repo-path",
            str(repo_dir),
            "--command",
            f"{sys.executable} fail.py",
            "--mode",
            "repair",
            "--confirm-apply",
            "--output-dir",
            str(output_dir),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["detected_failure_type"] == "external_env_failure"
    assert summary["final_status"] == "env_failed"
    assert summary["repair_plan"]["plan_type"] == "EnvRepairPlan"
