#!/usr/bin/env python3
"""Run a human-readable SciCodePilot showcase demo."""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict
from scicodepilot.repair.patch_plan import PatchPlan
from scicodepilot.review.patch_safety_reviewer import PatchSafetyReviewer


SOURCE_TASK_ID = "repair_tensor_shape_001"
ENV_TASK_ID = "repair_missing_module_003"


def section(title: str) -> None:
    print()
    print(f"=== {title} ===")


def one_line(text: str, limit: int = 180) -> str:
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


async def collect_events(
    controller: BackendController,
    task_id: str,
    mode: str,
    confirm_apply: bool = False,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    async for event in controller.run_task(
        task_id=task_id,
        mode=mode,
        confirm_apply=confirm_apply,
    ):
        events.append(event_to_dict(event))
    return events


def find_event(events: list[dict[str, Any]], event_type: str) -> dict[str, Any] | None:
    for event in events:
        if event.get("type") == event_type:
            return event
    return None


def print_failure_memory(events: list[dict[str, Any]]) -> None:
    failure = find_event(events, "FailureMemoryCreated")
    if not failure:
        print("- FailureMemory: not emitted")
        return

    print(f"- FailureMemory error_type: {failure.get('error_type')}")
    print(f"- Root cause hypothesis: {failure.get('root_cause_hypothesis')}")
    print(f"- Repair action: {failure.get('repair_action')}")
    evidence = failure.get("evidence") or []
    if evidence:
        print(f"- Evidence: {one_line(evidence[0])}")


def print_patch_and_review(events: list[dict[str, Any]]) -> None:
    patch = find_event(events, "PatchProposed")
    review = find_event(events, "PatchReviewCreated")
    approval = find_event(events, "PatchApprovalRequired")

    if patch:
        print(f"- PatchProposal target: {patch.get('target_file')}")
        print(f"- Proposed change: {patch.get('proposed_change')}")
        print(f"- Confidence: {patch.get('confidence')}")
    else:
        print("- PatchProposal: not emitted")

    if review:
        print(
            "- PatchReview: "
            f"approved={review.get('approved')} "
            f"blocked={review.get('blocked')} "
            f"risk={review.get('risk_level')}"
        )
        warnings = review.get("warnings") or []
        if warnings:
            print(f"- PatchReview warning: {one_line(warnings[0])}")
    else:
        print("- PatchReview: not emitted")

    if approval:
        print(f"- Approval gate: {approval.get('message')}")


def print_verification(events: list[dict[str, Any]]) -> None:
    applied = find_event(events, "PatchApplied")
    verification = find_event(events, "VerificationFinished")
    finished = find_event(events, "TaskFinished")

    if applied:
        print(
            "- PatchApplied: "
            f"success={applied.get('success')} target={applied.get('target_file')}"
        )
    if verification:
        print(
            "- Verification: "
            f"success={verification.get('success')} "
            f"return_code={verification.get('return_code')}"
        )
        print(f"- Verification summary: {verification.get('summary')}")
    if finished:
        print(f"- TaskFinished: {finished.get('status')} - {finished.get('summary')}")


def print_env_plan(events: list[dict[str, Any]]) -> None:
    plan = find_event(events, "EnvRepairPlanCreated")
    if not plan:
        print("- EnvRepairPlan: not emitted")
        return

    print(f"- EnvRepairPlan category: {plan.get('issue_category')}")
    print(f"- Summary: {plan.get('summary')}")
    print(f"- Requires user action: {plan.get('requires_user_action')}")
    for action in plan.get("suggested_actions") or []:
        print(f"- Suggested action: {action}")


def make_safety_case(name: str, target_file: str, diff: str) -> tuple[str, PatchPlan]:
    return (
        name,
        PatchPlan(
            task_id="showcase_safety_case",
            error_type="tensor_shape",
            target_file=target_file,
            suspected_line=4,
            rationale="Showcase safety stress case.",
            proposed_change="Demonstrate static safety review behavior.",
            unified_diff=diff,
            confidence=0.5,
        ),
    )


def print_safety_stress_summary() -> None:
    safe_diff = (
        "--- train.py\n"
        "+++ train.py\n"
        "@@\n"
        "-    classifier_expected_dim = 128\n"
        "+    classifier_expected_dim = 64\n"
    )
    unsafe_shell_diff = (
        "--- train.py\n"
        "+++ train.py\n"
        "@@\n"
        "-    pass\n"
        "+    os.system('rm -rf /tmp/demo')\n"
    )
    pip_install_diff = (
        "--- train.py\n"
        "+++ train.py\n"
        "@@\n"
        "-    pass\n"
        "+    # pip install missing-package\n"
    )

    cases = [
        make_safety_case("safe local tensor-shape patch", "train.py", safe_diff),
        make_safety_case("path traversal target", "../train.py", safe_diff),
        make_safety_case("unsafe shell deletion", "train.py", unsafe_shell_diff),
        make_safety_case("dependency install attempt", "train.py", pip_install_diff),
    ]

    reviewer = PatchSafetyReviewer()
    with tempfile.TemporaryDirectory() as workspace:
        blocked_count = 0
        for name, plan in cases:
            review = reviewer.review(plan, workspace)
            if review.blocked:
                blocked_count += 1
            print(
                "- "
                f"{name}: approved={review.approved} "
                f"blocked={review.blocked} risk={review.risk_level}"
            )
            if review.reasons:
                print(f"  reason: {one_line(review.reasons[0])}")

    print(f"- Safety stress summary: {blocked_count}/{len(cases)} cases blocked.")


async def main() -> None:
    print("SciCodePilot Showcase Demo")
    print("Scope: internal controlled benchmark only; no API key or public benchmark required.")
    print("Boundary: this is not a public benchmark and not a SOTA comparison.")

    controller = BackendController()

    section("1. Source-code repair diagnosis")
    diagnosis_events = await collect_events(controller, SOURCE_TASK_ID, "diagnosis")
    print(f"- Task: {SOURCE_TASK_ID}")
    print_failure_memory(diagnosis_events)

    section("2. Repair without apply")
    proposal_events = await collect_events(
        controller,
        SOURCE_TASK_ID,
        "repair",
        confirm_apply=False,
    )
    print_patch_and_review(proposal_events)
    print("- Workspace effect: patch is reviewed but not applied.")

    section("3. Repair with confirm apply")
    repair_events = await collect_events(
        controller,
        SOURCE_TASK_ID,
        "repair",
        confirm_apply=True,
    )
    print_verification(repair_events)
    print("- Workspace effect: changes occur only inside the isolated workspace.")

    section("4. EnvDoctor routing example")
    env_events = await collect_events(controller, ENV_TASK_ID, "repair")
    print(f"- Task: {ENV_TASK_ID}")
    print_env_plan(env_events)
    print("- Safety boundary: no automatic pip install and no fake data creation.")

    section("5. Safety stress cases")
    print_safety_stress_summary()

    section("6. Reproducibility and report assets")
    print("- Reproducibility manifest: report_assets/tables/repro_bundle_manifest.md")
    print("- Event flow figure: report_assets/figures/event_flow.md")
    print("- System pipeline figure: report_assets/figures/system_pipeline.md")
    print("- Benchmark distribution figure: report_assets/figures/benchmark_distribution.md")


if __name__ == "__main__":
    asyncio.run(main())
