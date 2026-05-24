import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.task_loader import BenchmarkTask
from scicodepilot.eval.task_loader import load_benchmark_task
from scicodepilot.events.bus import EventBus
from scicodepilot.llm.llm_client import LLMClient
from scicodepilot.repair.repair_policy import RepairPolicy
from scicodepilot.repair.repair_runner import RepairBenchmarkRunner


class DangerousPatchClient(LLMClient):
    async def complete(self, prompt: str) -> str:
        return (
            '{"target_file": "train.py", '
            '"rationale": "Dangerous test patch.", '
            '"proposed_change": "Add dangerous cleanup.", '
            '"unified_diff": "--- train.py\\n+++ train.py\\n@@\\n'
            '-    classifier_expected_dim = 128\\n'
            '+    os.system(\\"rm -rf /tmp/demo\\")\\n", '
            '"confidence": 0.9}'
        )


def create_fake_task(tmp_path) -> tuple[BenchmarkTask, Path]:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    train_path = repo_dir / "train.py"
    train_path.write_text(
        "import sys\n"
        "\n"
        "\n"
        "def main():\n"
        "    classifier_expected_dim = 128\n"
        "    if classifier_expected_dim == 128:\n"
        "        print(\"Loading synthetic dataset...\", flush=True)\n"
        "        print(\"Building tiny classifier head...\", flush=True)\n"
        "        print(\n"
        "            \"RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)\",\n"
        "            file=sys.stderr,\n"
        "            flush=True,\n"
        "        )\n"
        "        sys.exit(1)\n"
        "\n"
        "    print(\"Verification succeeded after patch.\", flush=True)\n"
        "\n"
        "\n"
        "if __name__ == \"__main__\":\n"
        "    main()\n",
        encoding="utf-8",
    )
    task = BenchmarkTask(
        task_id="fake_repair_tensor_shape_001",
        task_name="Fake repair tensor shape task",
        category="runtime_repair",
        difficulty="easy",
        entry_command=f"{sys.executable} train.py",
        task_dir=str(tmp_path),
        repo_dir=str(repo_dir),
        expected_diagnosis_path=str(tmp_path / "expected_diagnosis.json"),
        requires=[],
    )
    return task, train_path


async def run_fake_task(
    task: BenchmarkTask,
    policy: RepairPolicy | None = None,
    use_llm_planner: bool = False,
    llm_client: LLMClient | None = None,
):
    event_bus = EventBus()
    result = await RepairBenchmarkRunner(event_bus).run(
        task,
        policy=policy,
        use_llm_planner=use_llm_planner,
        llm_client=llm_client,
    )

    events = []
    for _ in range(event_bus.queue_size):
        events.append(await event_bus.next_event())

    return result, {event.type for event in events}


async def run_benchmark_task_with_events(
    task: BenchmarkTask,
    policy: RepairPolicy | None = None,
):
    event_bus = EventBus()
    result = await RepairBenchmarkRunner(event_bus).run(task, policy=policy)

    events = []
    for _ in range(event_bus.queue_size):
        events.append(await event_bus.next_event())

    return result, events


@pytest.mark.asyncio
async def test_repair_runner_default_requires_confirmation_and_does_not_apply(tmp_path) -> None:
    task, train_path = create_fake_task(tmp_path)

    result, event_types = await run_fake_task(task)

    assert result.patch_plan_generated is True
    assert result.requires_confirmation is True
    assert result.confirmation_granted is False
    assert result.patch_applied is False
    assert result.verification_success is False
    assert result.verification_return_code is None
    assert "PatchProposed" in event_types
    assert "PatchReviewCreated" in event_types
    assert "PatchApprovalRequired" in event_types
    assert "PatchApplied" not in event_types
    assert "VerificationStarted" not in event_types
    assert "VerificationFinished" not in event_types
    assert "TaskFinished" in event_types
    assert "classifier_expected_dim = 128" in train_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_repair_runner_applies_when_approved(tmp_path) -> None:
    task, train_path = create_fake_task(tmp_path)
    policy = RepairPolicy(require_confirmation=True, approved=True)

    result, event_types = await run_fake_task(task, policy)

    assert result.patch_plan_generated is True
    assert result.requires_confirmation is True
    assert result.confirmation_granted is True
    assert result.patch_applied is True
    assert result.verification_success is True
    assert result.verification_return_code == 0
    assert result.score == 1.0
    assert result.score_path is not None
    assert result.workspace_repo_dir is not None
    assert "PatchProposed" in event_types
    assert "PatchReviewCreated" in event_types
    assert "PatchApprovalRequired" not in event_types
    assert "PatchApplied" in event_types
    assert "VerificationStarted" in event_types
    assert "VerificationFinished" in event_types
    assert "TaskFinished" in event_types
    assert "classifier_expected_dim = 128" in train_path.read_text(encoding="utf-8")
    assert "classifier_expected_dim = 64" in (
        Path(result.workspace_repo_dir) / "train.py"
    ).read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_repair_runner_applies_when_confirmation_disabled(tmp_path) -> None:
    task, train_path = create_fake_task(tmp_path)
    policy = RepairPolicy(require_confirmation=False, approved=False)

    result, event_types = await run_fake_task(task, policy)

    assert result.patch_plan_generated is True
    assert result.requires_confirmation is False
    assert result.confirmation_granted is False
    assert result.patch_applied is True
    assert result.verification_success is True
    assert result.score == 1.0
    assert "PatchApprovalRequired" not in event_types
    assert "PatchReviewCreated" in event_types
    assert "PatchApplied" in event_types
    assert "classifier_expected_dim = 128" in train_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_repair_runner_missing_module_generates_env_repair_plan() -> None:
    task = load_benchmark_task("benchmark/tasks/repair_missing_module_003")
    policy = RepairPolicy(require_confirmation=True, approved=True)

    result, events = await run_benchmark_task_with_events(task, policy)
    event_types = {event.type for event in events}

    assert result.patch_plan_generated is False
    assert result.patch_applied is False
    assert result.verification_success is False
    assert result.env_repair_plan_generated is True
    assert result.env_issue_category == "dependency"
    assert "EnvRepairPlanCreated" in event_types
    assert "PatchApplied" not in event_types
    assert "VerificationFinished" not in event_types


@pytest.mark.asyncio
async def test_repair_runner_blocked_patch_does_not_apply(tmp_path) -> None:
    task, train_path = create_fake_task(tmp_path)
    policy = RepairPolicy(require_confirmation=True, approved=True)

    result, event_types = await run_fake_task(
        task,
        policy=policy,
        use_llm_planner=True,
        llm_client=DangerousPatchClient(),
    )

    assert result.patch_plan_generated is True
    assert result.patch_review_blocked is True
    assert result.patch_review_approved is False
    assert result.patch_applied is False
    assert result.verification_success is False
    assert "PatchProposed" in event_types
    assert "PatchReviewCreated" in event_types
    assert "PatchApprovalRequired" not in event_types
    assert "PatchApplied" not in event_types
    assert "VerificationStarted" not in event_types
    assert "classifier_expected_dim = 128" in train_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_repair_runner_missing_file_generates_env_repair_plan() -> None:
    task = load_benchmark_task("benchmark/tasks/repair_missing_file_004")
    policy = RepairPolicy(require_confirmation=True, approved=True)

    result, events = await run_benchmark_task_with_events(task, policy)
    event_types = {event.type for event in events}

    assert result.patch_plan_generated is False
    assert result.patch_applied is False
    assert result.verification_success is False
    assert result.env_repair_plan_generated is True
    assert result.env_issue_category == "data"
    assert "EnvRepairPlanCreated" in event_types
    assert "PatchApplied" not in event_types
    assert "VerificationFinished" not in event_types
