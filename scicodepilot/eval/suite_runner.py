from collections.abc import Callable

from scicodepilot.eval.diagnosis_runner import DiagnosisBenchmarkRunner
from scicodepilot.eval.suite_result import BenchmarkCaseResult, BenchmarkSuiteSummary
from scicodepilot.eval.task_loader import BenchmarkTask
from scicodepilot.events.bus import EventBus
from scicodepilot.repair.repair_policy import RepairPolicy
from scicodepilot.repair.repair_runner import RepairBenchmarkRunner


class BenchmarkSuiteRunner:
    """Run multiple benchmark tasks and convert results into flat records."""

    def __init__(self, event_bus_factory: Callable[[], EventBus] | None = None) -> None:
        self.event_bus_factory = event_bus_factory or EventBus

    async def run_tasks(
        self,
        tasks: list[BenchmarkTask],
        mode: str,
        confirm_apply: bool = False,
        use_llm_planner: bool = False,
    ) -> list[BenchmarkCaseResult]:
        if mode not in {"diagnosis", "repair"}:
            raise ValueError(f"Unsupported suite mode: {mode}")

        results: list[BenchmarkCaseResult] = []
        for task in tasks:
            try:
                if mode == "diagnosis":
                    results.append(await self._run_diagnosis_task(task))
                else:
                    results.append(
                        await self._run_repair_task(
                            task=task,
                            confirm_apply=confirm_apply,
                            use_llm_planner=use_llm_planner,
                        )
                    )
            except Exception as exc:
                results.append(
                    BenchmarkCaseResult(
                        task_id=task.task_id,
                        mode=mode,
                        message=f"Exception: {exc}",
                    )
                )

        return results

    async def _run_diagnosis_task(self, task: BenchmarkTask) -> BenchmarkCaseResult:
        event_bus = self.event_bus_factory()
        result = await DiagnosisBenchmarkRunner(event_bus).run(task)
        parsed_error_type = (
            result.parsed_error.error_type if result.parsed_error is not None else None
        )
        diagnosis_passed = (
            result.evaluation.passed if result.evaluation is not None else None
        )

        return BenchmarkCaseResult(
            task_id=task.task_id,
            mode="diagnosis",
            command_success=result.command_success,
            parsed_error_type=parsed_error_type,
            diagnosis_passed=diagnosis_passed,
            patch_plan_generated=result.patch_plan is not None,
            patch_applied=None,
            verification_success=None,
            verification_return_code=None,
            message=(
                "Diagnosis passed."
                if diagnosis_passed
                else "Diagnosis did not pass or was not evaluated."
            ),
        )

    async def _run_repair_task(
        self,
        task: BenchmarkTask,
        confirm_apply: bool,
        use_llm_planner: bool = False,
    ) -> BenchmarkCaseResult:
        event_bus = self.event_bus_factory()
        policy = RepairPolicy(require_confirmation=True, approved=confirm_apply)
        result = await RepairBenchmarkRunner(event_bus).run(
            task,
            policy=policy,
            use_llm_planner=use_llm_planner,
        )

        return BenchmarkCaseResult(
            task_id=task.task_id,
            mode="repair",
            command_success=None,
            parsed_error_type=None,
            diagnosis_passed=None,
            patch_plan_generated=result.patch_plan_generated,
            patch_applied=result.patch_applied,
            verification_success=result.verification_success,
            verification_return_code=result.verification_return_code,
            score=result.score,
            score_path=result.score_path,
            workspace_repo_dir=result.workspace_repo_dir,
            env_repair_plan_generated=result.env_repair_plan_generated,
            env_issue_category=result.env_issue_category,
            patch_review_approved=result.patch_review_approved,
            patch_review_blocked=result.patch_review_blocked,
            patch_review_risk_level=result.patch_review_risk_level,
            message=result.message,
        )


def summarize_results(
    results: list[BenchmarkCaseResult],
    mode: str,
) -> BenchmarkSuiteSummary:
    """Count key pass/apply/verification fields across case results."""
    scored_results = [result for result in results if result.score is not None]
    total_score = sum(result.score or 0.0 for result in scored_results)
    scored_task_count = len(scored_results)
    return BenchmarkSuiteSummary(
        total_tasks=len(results),
        mode=mode,
        diagnosis_pass_count=sum(result.diagnosis_passed is True for result in results),
        patch_plan_count=sum(result.patch_plan_generated is True for result in results),
        patch_applied_count=sum(result.patch_applied is True for result in results),
        verification_success_count=sum(
            result.verification_success is True for result in results
        ),
        total_score=total_score,
        average_score=total_score / scored_task_count if scored_task_count else 0.0,
        scored_task_count=scored_task_count,
        env_repair_plan_count=sum(
            result.env_repair_plan_generated is True for result in results
        ),
        patch_review_count=sum(
            result.patch_review_approved is not None for result in results
        ),
        patch_review_blocked_count=sum(
            result.patch_review_blocked is True for result in results
        ),
    )
