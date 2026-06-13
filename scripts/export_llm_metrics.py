from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"D:\Git\My_Git_Project\SciCodePilot\scicodepilot-dev-main"
)

INPUT_DIR = PROJECT_ROOT / "outputs" / "m30_llm_smoke" / "Summary_10_Tasks"

OUTPUT_DIR = Path(
    r"D:\Git\My_Git_Project\SciCodePilot\M30_Work\tables"
)

MODES = [
    "direct_llm",
    "structured_patchplan",
    "structured_patchplan_with_memory",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def parse_response_json(text: str) -> tuple[bool, dict[str, Any]]:
    """
    Try to parse LLM response as JSON.

    Some models may wrap JSON in markdown fences.
    This function handles:
    - raw JSON
    - ```json ... ```
    - ``` ... ```
    """
    if not text:
        return False, {}

    candidate = text.strip()

    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return True, parsed
        return False, {}
    except json.JSONDecodeError:
        return False, {}


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def analyze_one(task_id: str, mode: str, mode_dir: Path) -> dict[str, Any]:
    summary_path = mode_dir / "summary.json"
    response_path = mode_dir / "response.txt"
    prompt_path = mode_dir / "prompt.txt"

    summary = read_json(summary_path)
    response = read_text(response_path)

    valid_json, parsed_json = parse_response_json(response)

    valid_output = bool(response)
    api_call_success = summary.get("status") == "success"

    has_error_type = (
        "error_type" in parsed_json
        or contains_any(response, ["error type", "error_type", "错误类型"])
    )

    has_root_cause = (
        "root_cause_hypothesis" in parsed_json
        or contains_any(response, ["root cause", "root_cause", "原因", "cause"])
    )

    has_repair_action = (
        "repair_action" in parsed_json
        or contains_any(response, ["repair action", "repair suggestion", "修复", "suggestion"])
    )

    has_patch_steps = (
        "patch_plan_steps" in parsed_json
        or contains_any(response, ["patch_plan_steps", "step", "步骤"])
    )

    has_verification = (
        "verification_command" in parsed_json
        or contains_any(response, ["verification", "verify", "验证", "run the script"])
    )

    has_safety_risks = (
        "safety_review_field" in parsed_json
        or contains_any(response, ["safety", "review","field ","风险"])
    )

    has_memory_field = (
        "memory_usage" in parsed_json
        or contains_any(response, ["memory_usage", "failurememory", "memory"])
    )

    reviewable = (
        valid_json
        and has_error_type
        and has_root_cause
        and has_repair_action
    )

    unsafe_flag = "not_detected_by_rule"

    notes = []
    if not valid_output:
        notes.append("empty response")
    if mode == "direct_llm":
        notes.append("free-form natural language output")
    if mode in {"structured_patchplan", "structured_patchplan_with_memory"}:
        if valid_json:
            notes.append("valid JSON structured output")
        else:
            notes.append("structured mode but JSON parse failed")
    if mode == "structured_patchplan_with_memory":
        if has_memory_field:
            notes.append("memory field present")
        else:
            notes.append("memory field missing")

    return {
        "task_id": task_id,
        "mode": mode,
        "model": summary.get("model", ""),
        "api_call_success": api_call_success,
        "valid_output": valid_output,
        "valid_json": valid_json,
        "has_error_type": has_error_type,
        "has_root_cause": has_root_cause,
        "has_repair_action": has_repair_action,
        "has_patch_steps": has_patch_steps,
        "has_verification": has_verification,
        "has_safety_review_field": has_safety_review_field,
        "has_memory_field": has_memory_field,
        "reviewable": reviewable,
        "unsafe_flag": unsafe_flag,
        "verification_pass": "not_run",
        "latency": "not_recorded",
        "prompt_file": str(prompt_path),
        "response_file": str(response_path),
        "summary_file": str(summary_path),
        "notes": "; ".join(notes),
    }


def bool_to_int(value: bool) -> int:
    return 1 if value else 0


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_markdown_table(rows: list[dict[str, Any]]) -> str:
    headers = [
        "Task",
        "Mode",
        "API call",
        "Valid output",
        "Valid JSON",
        "Reviewable",
        "Repair steps",
        "Verification",
        "Safety review field",
        "Memory field",
        "Unsafe flag",
        "Verification pass",
        "Notes",
    ]

    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")

    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["task_id"],
                    row["mode"],
                    "PASS" if row["api_call_success"] else "FAIL",
                    "PASS" if row["valid_output"] else "FAIL",
                    "PASS" if row["valid_json"] else "N/A",
                    "PASS" if row["reviewable"] else "N/A",
                    "YES" if row["has_patch_steps"] else "NO",
                    "YES" if row["has_verification"] else "NO",
                    "YES" if row["has_safety_review_field"] else "NO",
                    "YES" if row["has_memory_field"] else "NO",
                    row["unsafe_flag"],
                    row["verification_pass"],
                    row["notes"],
                ]
            )
            + " |"
        )

    return "\n".join(lines)


def summarize_by_mode(rows: list[dict[str, Any]]) -> str:
    summary: dict[str, dict[str, int]] = {}

    for mode in MODES:
        mode_rows = [row for row in rows if row["mode"] == mode]
        summary[mode] = {
            "runs": len(mode_rows),
            "api_success": sum(bool_to_int(row["api_call_success"]) for row in mode_rows),
            "valid_output": sum(bool_to_int(row["valid_output"]) for row in mode_rows),
            "valid_json": sum(bool_to_int(row["valid_json"]) for row in mode_rows),
            "reviewable": sum(bool_to_int(row["reviewable"]) for row in mode_rows),
            "has_patch_steps": sum(bool_to_int(row["has_patch_steps"]) for row in mode_rows),
            "has_verification": sum(bool_to_int(row["has_verification"]) for row in mode_rows),
            "has_safety_review_field": sum(bool_to_int(row["has_safety_review_field"]) for row in mode_rows),
            "has_memory_field": sum(bool_to_int(row["has_memory_field"]) for row in mode_rows),
        }

    headers = [
        "Mode",
        "Runs",
        "API success",
        "Valid output",
        "Valid JSON",
        "Reviewable",
        "Patch steps",
        "Verification",
        "Safety review field",
        "Memory field",
    ]

    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")

    for mode, data in summary.items():
        lines.append(
            "| "
            + " | ".join(
                [
                    mode,
                    str(data["runs"]),
                    str(data["api_success"]),
                    str(data["valid_output"]),
                    str(data["valid_json"]),
                    str(data["reviewable"]),
                    str(data["has_patch_steps"]),
                    str(data["has_verification"]),
                    str(data["has_safety_review_field"]),
                    str(data["has_memory_field"]),
                ]
            )
            + " |"
        )

    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Input directory not found: {INPUT_DIR}")

    rows: list[dict[str, Any]] = []

    task_dirs = sorted(
        path for path in INPUT_DIR.iterdir()
        if path.is_dir() and path.name.startswith("repair_")
    )

    for task_dir in task_dirs:
        task_id = task_dir.name

        for mode in MODES:
            mode_dir = task_dir / mode
            if not mode_dir.exists():
                rows.append(
                    {
                        "task_id": task_id,
                        "mode": mode,
                        "model": "",
                        "api_call_success": False,
                        "valid_output": False,
                        "valid_json": False,
                        "has_error_type": False,
                        "has_root_cause": False,
                        "has_repair_action": False,
                        "has_patch_steps": False,
                        "has_verification": False,
                        "has_safety_review_field": False,
                        "has_memory_field": False,
                        "reviewable": False,
                        "unsafe_flag": "not_detected_by_rule",
                        "verification_pass": "not_run",
                        "latency": "not_recorded",
                        "prompt_file": "",
                        "response_file": "",
                        "summary_file": "",
                        "notes": "mode directory missing",
                    }
                )
                continue

            rows.append(analyze_one(task_id, mode, mode_dir))

    csv_path = OUTPUT_DIR / "m30_llm_mode_metrics.csv"
    detail_md_path = OUTPUT_DIR / "m30_llm_mode_metrics.md"
    summary_md_path = OUTPUT_DIR / "m30_llm_mode_summary.md"

    write_csv(rows, csv_path)

    detail_md_path.write_text(
        "# M30 LLM Mode Metrics\n\n" + make_markdown_table(rows),
        encoding="utf-8",
    )

    summary_md_path.write_text(
        "# M30 LLM Mode Summary\n\n" + summarize_by_mode(rows),
        encoding="utf-8",
    )

    print(f"Input directory: {INPUT_DIR}")
    print(f"Rows exported: {len(rows)}")
    print(f"CSV written to: {csv_path}")
    print(f"Detail table written to: {detail_md_path}")
    print(f"Summary table written to: {summary_md_path}")


if __name__ == "__main__":
    main()