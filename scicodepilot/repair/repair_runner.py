import asyncio

from scicodepilot.eval.hidden_evaluator import HiddenEvaluator
from scicodepilot.eval.task_loader import BenchmarkTask
from scicodepilot.eval.workspace import WorkspaceManager
from scicodepilot.env.env_doctor import EnvDoctor
from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import (
    EnvRepairPlanCreated,
    ErrorDetected,
    FailureMemoryCreated,
    PatchApprovalRequired,
    PatchApplied,
    PatchProposed,
    PatchReviewCreated,
    PlanCreated,
    StepStarted,
    TaskFinished,
    TaskStarted,
    VerificationFinished,
    VerificationStarted,
)
from scicodepilot.llm.llm_client import LLMClient, create_llm_client_from_env
from scicodepilot.llm.llm_patch_planner import LLMPatchPlanner
from scicodepilot.memory.failure_memory import FailureMemoryBuilder
from scicodepilot.repair.patch_applier import PatchApplier
from scicodepilot.repair.patch_planner import PatchPlanner
from scicodepilot.repair.repair_policy import RepairPolicy
from scicodepilot.repair.repair_result import RepairResult
from scicodepilot.review.patch_safety_reviewer import PatchSafetyReviewer
from scicodepilot.tools.shell_tool import ShellTool
from scicodepilot.tools.traceback_parser import TracebackParser


class RepairBenchmarkRunner:
    """Run diagnosis, patch application, verification, and restoration."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def run(
        self,
        task: BenchmarkTask,
        policy: RepairPolicy | None = None,
        use_llm_planner: bool = False,
        llm_client: LLMClient | None = None,
    ) -> RepairResult:
        if policy is None:
            policy = RepairPolicy()

        shell_tool = ShellTool(self.event_bus)
        parser = TracebackParser()
        memory_builder = FailureMemoryBuilder()
        patch_planner = PatchPlanner()
        env_doctor = EnvDoctor()
        patch_applier = PatchApplier()
        patch_safety_reviewer = PatchSafetyReviewer()
        workspace = WorkspaceManager().create_workspace(task)
        workspace_repo_dir = workspace.workspace_repo_dir

        await self.event_bus.emit(
            TaskStarted(task_id=task.task_id, task_name=task.task_name)
        )
        await asyncio.sleep(0.15)

        await self.event_bus.emit(
            PlanCreated(
                task_id=task.task_id,
                steps=[
                    "Run the original benchmark command",
                    "Parse runtime failure",
                    "Generate structured failure memory",
                    "Generate patch plan",
                    "Apply patch plan",
                    "Run verification command",
                    "Restore original benchmark file",
                ],
            )
        )
        await asyncio.sleep(0.15)

        await self.event_bus.emit(
            StepStarted(
                task_id=task.task_id,
                step_index=1,
                step_name="Run the original benchmark command",
            )
        )
        original_result = await shell_tool.run(
            task_id=task.task_id,
            command=task.entry_command,
            cwd=workspace_repo_dir,
        )

        if original_result.success:
            message = "Original benchmark command succeeded; no repair was required."
            await self.event_bus.emit(
                TaskFinished(task_id=task.task_id, status="success", summary=message)
            )
            return RepairResult(
                task_id=task.task_id,
                patch_applied=False,
                target_file=None,
                verification_command=task.entry_command,
                verification_success=True,
                verification_return_code=original_result.return_code,
                message=message,
                requires_confirmation=policy.require_confirmation,
                confirmation_granted=policy.approved,
                workspace_repo_dir=workspace_repo_dir,
            )

        await self.event_bus.emit(
            StepStarted(
                task_id=task.task_id,
                step_index=2,
                step_name="Parse runtime failure",
            )
        )
        parsed_error = parser.parse(original_result.stderr_lines)
        if parsed_error is None:
            await self.event_bus.emit(
                ErrorDetected(
                    task_id=task.task_id,
                    error_type="unknown_error",
                    summary=(
                        "The command failed, but no known parser rule matched "
                        "the stderr output."
                    ),
                    evidence=original_result.stderr_lines,
                )
            )
            await self.event_bus.emit(
                TaskFinished(
                    task_id=task.task_id,
                    status="failed",
                    summary="Repair workflow stopped because no known diagnosis rule matched.",
                )
            )
            return RepairResult(
                task_id=task.task_id,
                patch_applied=False,
                target_file=None,
                verification_command=task.entry_command,
                verification_success=False,
                verification_return_code=None,
                message="No known diagnosis rule matched.",
                requires_confirmation=policy.require_confirmation,
                confirmation_granted=policy.approved,
                workspace_repo_dir=workspace_repo_dir,
            )

        await self.event_bus.emit(
            ErrorDetected(
                task_id=task.task_id,
                error_type=parsed_error.error_type,
                summary=parsed_error.summary,
                evidence=parsed_error.evidence,
            )
        )

        await self.event_bus.emit(
            StepStarted(
                task_id=task.task_id,
                step_index=3,
                step_name="Generate structured failure memory",
            )
        )
        failure_memory = memory_builder.from_parsed_error(parsed_error)
        await self.event_bus.emit(
            FailureMemoryCreated(
                task_id=task.task_id,
                error_type=failure_memory.error_type,
                evidence=failure_memory.evidence,
                root_cause_hypothesis=failure_memory.root_cause_hypothesis,
                repair_action=failure_memory.repair_action,
            )
        )

        await self.event_bus.emit(
            StepStarted(
                task_id=task.task_id,
                step_index=4,
                step_name="Generate patch plan",
            )
        )
        patch_plan = await self._create_patch_plan(
            task_id=task.task_id,
            repo_dir=workspace_repo_dir,
            parsed_error=parsed_error,
            failure_memory=failure_memory,
            rule_planner=patch_planner,
            use_llm_planner=use_llm_planner,
            llm_client=llm_client,
        )
        if patch_plan is None:
            env_repair_plan = env_doctor.create_plan(
                task_id=task.task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
            )
            if env_repair_plan is not None:
                message = (
                    "Source-code patch was not generated; an environment/data "
                    "repair plan was generated and user action is required."
                )
                await self.event_bus.emit(
                    EnvRepairPlanCreated(
                        task_id=task.task_id,
                        error_type=env_repair_plan.error_type,
                        issue_category=env_repair_plan.issue_category,
                        summary=env_repair_plan.summary,
                        suggested_actions=env_repair_plan.suggested_actions,
                        requires_user_action=env_repair_plan.requires_user_action,
                        confidence=env_repair_plan.confidence,
                    )
                )
                await self.event_bus.emit(
                    TaskFinished(
                        task_id=task.task_id,
                        status="failed",
                        summary=message,
                    )
                )
                return RepairResult(
                    task_id=task.task_id,
                    patch_applied=False,
                    target_file=None,
                    verification_command=(
                        env_repair_plan.verification_command or task.entry_command
                    ),
                    verification_success=False,
                    verification_return_code=None,
                    message=message,
                    patch_plan_generated=False,
                    requires_confirmation=policy.require_confirmation,
                    confirmation_granted=policy.approved,
                    workspace_repo_dir=workspace_repo_dir,
                    env_repair_plan_generated=True,
                    env_issue_category=env_repair_plan.issue_category,
                )

            await self.event_bus.emit(
                PatchApplied(
                    task_id=task.task_id,
                    target_file=None,
                    success=False,
                    message="No patch plan was generated; repair skipped.",
                    unified_diff=None,
                )
            )
            await self.event_bus.emit(
                TaskFinished(
                    task_id=task.task_id,
                    status="failed",
                    summary="Repair workflow stopped because no patch plan was generated.",
                )
            )
            return RepairResult(
                task_id=task.task_id,
                patch_applied=False,
                target_file=None,
                verification_command=task.entry_command,
                verification_success=False,
                verification_return_code=None,
                message="No patch plan was generated.",
                requires_confirmation=policy.require_confirmation,
                confirmation_granted=policy.approved,
                workspace_repo_dir=workspace_repo_dir,
            )

        await self.event_bus.emit(
            PatchProposed(
                task_id=task.task_id,
                target_file=patch_plan.target_file,
                suspected_line=patch_plan.suspected_line,
                confidence=patch_plan.confidence,
                proposed_change=patch_plan.proposed_change,
                unified_diff=patch_plan.unified_diff,
            )
        )

        patch_review = patch_safety_reviewer.review(patch_plan, workspace_repo_dir)
        await self.event_bus.emit(
            PatchReviewCreated(
                task_id=task.task_id,
                approved=patch_review.approved,
                blocked=patch_review.blocked,
                risk_level=patch_review.risk_level,
                reasons=patch_review.reasons,
                warnings=patch_review.warnings,
            )
        )

        if patch_review.blocked or not patch_review.approved:
            message = "Patch was blocked by safety reviewer; repair was not applied."
            await self.event_bus.emit(
                TaskFinished(
                    task_id=task.task_id,
                    status="failed",
                    summary=message,
                )
            )
            return RepairResult(
                task_id=task.task_id,
                patch_applied=False,
                target_file=patch_plan.target_file,
                verification_command=task.entry_command,
                verification_success=False,
                verification_return_code=None,
                message=message,
                patch_plan_generated=True,
                requires_confirmation=policy.require_confirmation,
                confirmation_granted=policy.approved,
                workspace_repo_dir=workspace_repo_dir,
                patch_review_approved=patch_review.approved,
                patch_review_blocked=patch_review.blocked,
                patch_review_risk_level=patch_review.risk_level,
            )

        if not policy.can_apply_patch():
            message = (
                "Patch plan generated, but patch application requires explicit "
                "confirmation."
            )
            await self.event_bus.emit(
                PatchApprovalRequired(
                    task_id=task.task_id,
                    target_file=patch_plan.target_file,
                    message="Patch application requires explicit confirmation.",
                    unified_diff=patch_plan.unified_diff,
                )
            )
            await self.event_bus.emit(
                TaskFinished(
                    task_id=task.task_id,
                    status="demo_finished",
                    summary=(
                        "Patch plan was generated, but patch application requires "
                        "explicit confirmation."
                    ),
                )
            )
            return RepairResult(
                task_id=task.task_id,
                patch_applied=False,
                target_file=patch_plan.target_file,
                verification_command=task.entry_command,
                verification_success=False,
                verification_return_code=None,
                message=message,
                patch_plan_generated=True,
                requires_confirmation=policy.require_confirmation,
                confirmation_granted=policy.approved,
                workspace_repo_dir=workspace_repo_dir,
                patch_review_approved=patch_review.approved,
                patch_review_blocked=patch_review.blocked,
                patch_review_risk_level=patch_review.risk_level,
            )

        await self.event_bus.emit(
            StepStarted(
                task_id=task.task_id,
                step_index=5,
                step_name="Apply patch plan",
            )
        )
        repair_result: RepairResult | None = None

        try:
            patch_applied = patch_applier.apply(workspace_repo_dir, patch_plan)
            await self.event_bus.emit(
                PatchApplied(
                    task_id=task.task_id,
                    target_file=patch_plan.target_file,
                    success=patch_applied,
                    message=(
                        "Patch plan was applied successfully."
                        if patch_applied
                        else "Patch plan could not be applied."
                    ),
                    unified_diff=patch_plan.unified_diff,
                )
            )

            if not patch_applied:
                repair_result = RepairResult(
                    task_id=task.task_id,
                    patch_applied=False,
                    target_file=patch_plan.target_file,
                    verification_command=task.entry_command,
                    verification_success=False,
                    verification_return_code=None,
                    message="Patch application failed.",
                    patch_plan_generated=True,
                    requires_confirmation=policy.require_confirmation,
                    confirmation_granted=policy.approved,
                    workspace_repo_dir=workspace_repo_dir,
                    patch_review_approved=patch_review.approved,
                    patch_review_blocked=patch_review.blocked,
                    patch_review_risk_level=patch_review.risk_level,
                )
                await self.event_bus.emit(
                    TaskFinished(
                        task_id=task.task_id,
                        status="failed",
                        summary="Repair workflow stopped because patch application failed.",
                    )
                )
                return repair_result

            await self.event_bus.emit(
                StepStarted(
                    task_id=task.task_id,
                    step_index=6,
                    step_name="Run verification command",
                )
            )
            await self.event_bus.emit(
                VerificationStarted(
                    task_id=task.task_id,
                    command=task.entry_command,
                    cwd=workspace_repo_dir,
                )
            )
            verification_result = await shell_tool.run(
                task_id=task.task_id,
                command=task.entry_command,
                cwd=workspace_repo_dir,
            )
            await self.event_bus.emit(
                VerificationFinished(
                    task_id=task.task_id,
                    command=task.entry_command,
                    return_code=verification_result.return_code,
                    success=verification_result.success,
                    summary=(
                        "Verification command succeeded."
                        if verification_result.success
                        else "Verification command failed after patch application."
                    ),
                )
            )
            score_result = await HiddenEvaluator().evaluate(task, workspace_repo_dir)

            repair_result = RepairResult(
                task_id=task.task_id,
                patch_applied=True,
                target_file=patch_plan.target_file,
                verification_command=task.entry_command,
                verification_success=verification_result.success,
                verification_return_code=verification_result.return_code,
                message=(
                    "Patch was applied and verification command succeeded."
                    if verification_result.success
                    else "Patch was applied but verification command still failed."
                ),
                patch_plan_generated=True,
                requires_confirmation=policy.require_confirmation,
                confirmation_granted=policy.approved,
                score=score_result.score,
                score_path=score_result.score_path,
                workspace_repo_dir=workspace_repo_dir,
                patch_review_approved=patch_review.approved,
                patch_review_blocked=patch_review.blocked,
                patch_review_risk_level=patch_review.risk_level,
            )

            await self.event_bus.emit(
                StepStarted(
                    task_id=task.task_id,
                    step_index=7,
                    step_name="Restore original benchmark file",
                )
            )
            return repair_result
        finally:
            if repair_result is not None and repair_result.patch_applied:
                await self.event_bus.emit(
                    TaskFinished(
                        task_id=task.task_id,
                        status="success" if repair_result.verification_success else "failed",
                        summary=(
                            "Repair workflow completed successfully; original benchmark file was restored."
                            if repair_result.verification_success
                            else "Repair workflow completed but verification failed; original benchmark file was restored."
                        ),
                    )
                )

    async def _create_patch_plan(
        self,
        task_id: str,
        repo_dir: str,
        parsed_error,
        failure_memory,
        rule_planner: PatchPlanner,
        use_llm_planner: bool,
        llm_client: LLMClient | None,
    ):
        if use_llm_planner:
            try:
                llm_planner = LLMPatchPlanner(
                    client=llm_client or create_llm_client_from_env()
                )
                llm_plan = await llm_planner.create_plan(
                    task_id=task_id,
                    parsed_error=parsed_error,
                    failure_memory=failure_memory,
                    repo_dir=repo_dir,
                )
                if llm_plan is not None:
                    return llm_plan
            except Exception:
                pass

        return rule_planner.create_plan(
            task_id=task_id,
            repo_dir=repo_dir,
            parsed_error=parsed_error,
            failure_memory=failure_memory,
        )
