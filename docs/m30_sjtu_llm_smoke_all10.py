import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\Git\My_Git_Project\SciCodePilot\scicodepilot-dev-main")
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "m30_llm_smoke" / datetime.now().strftime("%Y%m%d_%H%M%S")

BASE_URL = os.environ["SJTU_API_BASE_URL"].rstrip("/")
API_KEY = os.environ["SJTU_API_KEY"]
MODEL = os.environ.get("SJTU_MODEL", "deepseek-chat")

TASKS = [
    "repair_loss_input_008",
    "repair_collate_fn_009",
]

MODES = [
    "direct_llm",
    "structured_patchplan",
    "structured_patchplan_with_memory",
]


def read_task_files(task_id: str) -> str:
    task_dir = PROJECT_ROOT / "benchmark" / "tasks" / task_id
    parts = []

    for path in sorted(task_dir.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".py", ".json", ".txt"}:
            try:
                rel = path.relative_to(task_dir)
                text = path.read_text(encoding="utf-8")
                parts.append(f"\n\n# FILE: {rel}\n{text}")
            except UnicodeDecodeError:
                continue

    return "".join(parts)


def build_prompt(task_id: str, mode: str, task_files: str) -> str:
    if mode == "direct_llm":
        return f"""
You are evaluating a scientific Python code repair benchmark.

Task ID: {task_id}

Read the task files and provide:
1. likely error type
2. root cause
3. repair suggestion
4. verification idea

Return concise plain text.

TASK FILES:
{task_files}
"""

    if mode == "structured_patchplan":
        return f"""
You are SciCodePilot's structured repair planner.

Task ID: {task_id}

Read the task files and output ONLY valid JSON.

Schema:
{{
  "task_id": "{task_id}",
  "error_type": "string",
  "root_cause_hypothesis": "string",
  "repair_action": "string",
  "patch_plan_steps": ["string"],
  "safety_risks": ["string"],
  "verification_command": "string"
}}

TASK FILES:
{task_files}
"""

    return f"""
You are SciCodePilot's memory-augmented structured repair planner.

Task ID: {task_id}

Use the following retrieved FailureMemory as in-context guidance:
- Similar failures often require matching the error type, root cause, repair action, and verification command.
- For source bugs, propose minimal source edits.
- For environment/data bugs, do not propose unsafe source patches.

Output ONLY valid JSON.

Schema:
{{
  "task_id": "{task_id}",
  "error_type": "string",
  "root_cause_hypothesis": "string",
  "repair_action": "string",
  "patch_plan_steps": ["string"],
  "safety_risks": ["string"],
  "verification_command": "string",
  "memory_usage": "string"
}}

TASK FILES:
{task_files}
"""


def call_llm(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a careful code repair planner. Follow the user's output format exactly.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }

    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url=f"{BASE_URL}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"]


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    results = []

    for task_id in TASKS:
        task_files = read_task_files(task_id)

        for mode in MODES:
            run_dir = OUTPUT_ROOT / task_id / mode
            run_dir.mkdir(parents=True, exist_ok=True)

            prompt = build_prompt(task_id, mode, task_files)
            (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

            try:
                response = call_llm(prompt)
                status = "success"
            except Exception as exc:
                response = f"{type(exc).__name__}: {exc}"
                status = "failed"

            (run_dir / "response.txt").write_text(response, encoding="utf-8")

            summary = {
                "task_id": task_id,
                "mode": mode,
                "model": MODEL,
                "status": status,
                "prompt_file": str(run_dir / "prompt.txt"),
                "response_file": str(run_dir / "response.txt"),
            }

            (run_dir / "summary.json").write_text(
                json.dumps(summary, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            results.append(summary)
            print(f"{task_id} | {mode} | {status}")

    (OUTPUT_ROOT / "run_summary.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved outputs to: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()