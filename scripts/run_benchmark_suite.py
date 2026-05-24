import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.suite_runner import BenchmarkSuiteRunner, summarize_results
from scicodepilot.eval.task_loader import BenchmarkTask, load_benchmark_task


def discover_tasks(selected_task_ids: list[str] | None = None) -> list[BenchmarkTask]:
    tasks_root = PROJECT_ROOT / "benchmark" / "tasks"
    selected = set(selected_task_ids or [])
    tasks: list[BenchmarkTask] = []

    for metadata_path in sorted(tasks_root.glob("*/metadata.json")):
        task = load_benchmark_task(metadata_path.parent)
        if selected and task.task_id not in selected:
            continue
        tasks.append(task)

    return tasks


def model_to_dict(model) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def write_results(output_dir: Path, results, summary) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.jsonl"
    summary_path = output_dir / "summary.json"

    with results_path.open("w", encoding="utf-8") as file:
        for result in results:
            file.write(json.dumps(model_to_dict(result), ensure_ascii=False) + "\n")

    summary_path.write_text(
        json.dumps(model_to_dict(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def print_summary(summary, output_dir: Path) -> None:
    print()
    print("=== Benchmark Suite Summary ===")
    print(f"mode: {summary.mode}")
    print(f"total_tasks: {summary.total_tasks}")
    print(f"diagnosis_pass_count: {summary.diagnosis_pass_count}")
    print(f"patch_plan_count: {summary.patch_plan_count}")
    print(f"patch_review_count: {summary.patch_review_count}")
    print(f"patch_review_blocked_count: {summary.patch_review_blocked_count}")
    print(f"patch_applied_count: {summary.patch_applied_count}")
    print(f"verification_success_count: {summary.verification_success_count}")
    print(f"scored_task_count: {summary.scored_task_count}")
    print(f"env_repair_plan_count: {summary.env_repair_plan_count}")
    print(f"total_score: {summary.total_score}")
    print(f"average_score: {summary.average_score}")
    print(f"output_dir: {output_dir}")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["diagnosis", "repair"],
        default="diagnosis",
    )
    parser.add_argument("--confirm-apply", action="store_true")
    parser.add_argument("--use-llm-planner", action="store_true")
    parser.add_argument("--tasks", nargs="*")
    parser.add_argument("--output-dir", default="outputs/benchmark_runs")
    args = parser.parse_args()

    tasks = discover_tasks(args.tasks)
    runner = BenchmarkSuiteRunner()
    results = await runner.run_tasks(
        tasks=tasks,
        mode=args.mode,
        confirm_apply=args.confirm_apply,
        use_llm_planner=args.use_llm_planner,
    )
    if args.use_llm_planner:
        print("LLM patch planner enabled; using configured client or deterministic mock mode.")
    summary = summarize_results(results, args.mode)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / args.output_dir / timestamp
    write_results(output_dir, results, summary)
    print_summary(summary, output_dir)


if __name__ == "__main__":
    asyncio.run(main())
