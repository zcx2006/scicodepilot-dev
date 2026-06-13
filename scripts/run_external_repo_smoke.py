#!/usr/bin/env python3
"""Run smoke diagnosis or repair planning for a local external Python repo."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.env.env_doctor import EnvDoctor
from scicodepilot.memory.failure_memory import FailureMemoryBuilder
from scicodepilot.repair.patch_planner import PatchPlanner
from scicodepilot.review.patch_safety_reviewer import PatchSafetyReviewer
from scicodepilot.tools.traceback_parser import ParsedError, TracebackParser


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SciCodePilot external repo smoke diagnosis or repair planning."
    )
    parser.add_argument("--repo-path", required=True, help="Path to a local Python repo.")
    parser.add_argument("--command", required=True, help="Command to run in the copied workspace.")
    parser.add_argument(
        "--mode",
        choices=["diagnosis", "repair-plan"],
        default="diagnosis",
        help="Run diagnosis only or non-applying repair planning.",
    )
    parser.add_argument(
        "--copy-workspace",
        action="store_true",
        default=True,
        help="Copy the repo into an isolated workspace before running. Enabled by default.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory. Defaults to outputs/external_smoke/<timestamp>.",
    )
    return parser.parse_args()


def model_to_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()


def create_output_dir(raw_output_dir: str | None) -> Path:
    if raw_output_dir:
        output_dir = Path(raw_output_dir)
        if not output_dir.is_absolute():
            output_dir = PROJECT_ROOT / output_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = PROJECT_ROOT / "outputs" / "external_smoke" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def copy_repo(repo_path: Path, workspace_dir: Path) -> None:
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)

    def ignore(_dir: str, names: list[str]) -> set[str]:
        ignored = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
        return {name for name in names if name in ignored}

    shutil.copytree(repo_path, workspace_dir, ignore=ignore)


def run_command(command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )


def parse_failure(stderr: str, stdout: str) -> ParsedError:
    stderr_lines = [line for line in stderr.splitlines() if line.strip()]
    parsed = TracebackParser().parse(stderr_lines)
    if parsed is not None:
        return parsed

    evidence_source = stderr_lines or [line for line in stdout.splitlines() if line.strip()]
    evidence = evidence_source[-3:] if evidence_source else ["No traceback evidence captured."]
    return ParsedError(
        error_type="unsupported_external_failure",
        summary=(
            "The command failed, but the current external repo smoke interface "
            "does not have a specialized parser rule for this failure."
        ),
        evidence=evidence,
    )


def build_repair_plan(
    workspace_dir: Path,
    parsed_error: ParsedError,
    failure_memory,
) -> dict[str, Any]:
    task_id = "external_repo_smoke"
    env_plan = EnvDoctor().create_plan(task_id, parsed_error, failure_memory)
    if env_plan is not None:
        return {
            "plan_type": "EnvRepairPlan",
            "env_repair_plan": model_to_dict(env_plan),
            "note": "Environment/data plan only; no patch was applied.",
        }

    if parsed_error.error_type == "unsupported_external_failure":
        return {
            "plan_type": "no_op",
            "note": (
                "unsupported_external_failure: current system can only generate "
                "a diagnosis summary or no-op plan for this external failure."
            ),
        }

    try:
        patch_plan = PatchPlanner().create_plan(
            task_id=task_id,
            repo_dir=str(workspace_dir),
            parsed_error=parsed_error,
            failure_memory=failure_memory,
        )
    except (FileNotFoundError, UnicodeDecodeError) as exc:
        return {
            "plan_type": "no_op",
            "note": (
                "No patch plan generated for this external repo layout. "
                f"Reason: {type(exc).__name__}: {exc}"
            ),
        }

    if patch_plan is None:
        return {
            "plan_type": "no_op",
            "note": "No source-code patch plan is available for this external failure type.",
        }

    patch_review = PatchSafetyReviewer().review(patch_plan, str(workspace_dir))
    return {
        "plan_type": "PatchPlan",
        "patch_plan": model_to_dict(patch_plan),
        "patch_review": model_to_dict(patch_review),
        "note": "Patch was reviewed only; no patch was applied.",
    }


def build_summary(args: argparse.Namespace, output_dir: Path, workspace_dir: Path) -> dict[str, Any]:
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        raise FileNotFoundError(f"repo-path must be an existing directory: {repo_path}")

    copy_repo(repo_path, workspace_dir)
    result = run_command(args.command, workspace_dir)

    command_record = {
        "command": args.command,
        "return_code": result.returncode,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

    if result.returncode == 0:
        parsed_error = ParsedError(
            error_type="no_failure",
            summary="Command completed successfully; no failure diagnosis was needed.",
            evidence=[],
        )
    else:
        parsed_error = parse_failure(result.stderr, result.stdout)

    failure_memory = FailureMemoryBuilder().from_parsed_error(parsed_error)
    summary: dict[str, Any] = {
        "mode": args.mode,
        "repo_path": str(repo_path),
        "output_dir": str(output_dir),
        "workspace_dir": str(workspace_dir),
        "copy_workspace": True,
        "original_repo_mutated": False,
        "command": command_record,
        "parsed_error": model_to_dict(parsed_error),
        "failure_memory": model_to_dict(failure_memory),
        "scope_note": (
            "External repo smoke interface only; not a public benchmark result "
            "and not a SOTA comparison."
        ),
    }

    if args.mode == "repair-plan" and result.returncode != 0:
        summary["repair_plan"] = build_repair_plan(
            workspace_dir,
            parsed_error,
            failure_memory,
        )
    elif args.mode == "repair-plan":
        summary["repair_plan"] = {
            "plan_type": "no_op",
            "note": "Command succeeded, so no repair plan was generated.",
        }

    return summary


def line(text: str, limit: int = 180) -> str:
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def build_markdown(summary: dict[str, Any]) -> str:
    parsed = summary["parsed_error"]
    memory = summary["failure_memory"]
    command = summary["command"]
    lines = [
        "# External Repo Smoke Summary",
        "",
        f"- Mode: `{summary['mode']}`",
        f"- Repo path: `{summary['repo_path']}`",
        f"- Workspace dir: `{summary['workspace_dir']}`",
        f"- Command: `{command['command']}`",
        f"- Return code: `{command['return_code']}`",
        f"- Scope: {summary['scope_note']}",
        "",
        "## Diagnosis",
        "",
        f"- Error type: `{parsed['error_type']}`",
        f"- Summary: {parsed['summary']}",
        "- Evidence:",
    ]

    evidence = parsed.get("evidence") or ["None"]
    lines.extend(f"  - {line(item)}" for item in evidence)

    lines.extend(
        [
            "",
            "## FailureMemory",
            "",
            f"- Error type: `{memory['error_type']}`",
            f"- Root cause hypothesis: {memory['root_cause_hypothesis']}",
            f"- Repair action: {memory['repair_action']}",
        ]
    )

    repair_plan = summary.get("repair_plan")
    if repair_plan:
        lines.extend(["", "## Repair Planning", ""])
        lines.append(f"- Plan type: `{repair_plan['plan_type']}`")
        lines.append(f"- Note: {repair_plan.get('note', '')}")
        if repair_plan["plan_type"] == "EnvRepairPlan":
            env_plan = repair_plan["env_repair_plan"]
            lines.append(f"- EnvRepairPlan category: `{env_plan['issue_category']}`")
            lines.append(f"- EnvRepairPlan summary: {env_plan['summary']}")
        if repair_plan["plan_type"] == "PatchPlan":
            patch_plan = repair_plan["patch_plan"]
            patch_review = repair_plan["patch_review"]
            lines.append(f"- PatchPlan target: `{patch_plan['target_file']}`")
            lines.append(f"- PatchPlan change: {patch_plan['proposed_change']}")
            lines.append(
                "- PatchSafetyReviewer: "
                f"approved={patch_review['approved']} "
                f"blocked={patch_review['blocked']} "
                f"risk={patch_review['risk_level']}"
            )

    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- The original repo was copied before execution.",
            "- No patch was applied to the original repo.",
            "- This smoke result is not a public benchmark result.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(output_dir: Path, summary: dict[str, Any]) -> None:
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "summary.md").write_text(build_markdown(summary), encoding="utf-8")


def print_console_summary(summary: dict[str, Any]) -> None:
    parsed = summary["parsed_error"]
    memory = summary["failure_memory"]
    command = summary["command"]
    print("SciCodePilot External Repo Smoke")
    print(f"- Mode: {summary['mode']}")
    print(f"- Workspace: {summary['workspace_dir']}")
    print(f"- Command return code: {command['return_code']}")
    print(f"- Error type: {parsed['error_type']}")
    print(f"- Evidence: {line((parsed.get('evidence') or ['None'])[0])}")
    print(f"- FailureMemory: {memory['root_cause_hypothesis']}")
    if "repair_plan" in summary:
        repair_plan = summary["repair_plan"]
        print(f"- Repair planning: {repair_plan['plan_type']} - {repair_plan.get('note', '')}")
    print(f"- summary.md: {Path(summary['output_dir']) / 'summary.md'}")
    print(f"- summary.json: {Path(summary['output_dir']) / 'summary.json'}")


def main() -> int:
    args = parse_args()
    output_dir = create_output_dir(args.output_dir)
    workspace_dir = output_dir / "workspace"
    summary = build_summary(args, output_dir, workspace_dir)
    write_outputs(output_dir, summary)
    print_console_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
