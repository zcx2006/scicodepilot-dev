import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.task_loader import BenchmarkTask
from scicodepilot.events.bus import EventBus
from scicodepilot.llm.llm_client import LLMClient, MockLLMClient
from scicodepilot.llm.llm_patch_planner import LLMPatchPlanner
from scicodepilot.memory.failure_memory import FailureMemoryBuilder
from scicodepilot.repair.repair_policy import RepairPolicy
from scicodepilot.repair.repair_runner import RepairBenchmarkRunner
from scicodepilot.tools.traceback_parser import ParsedError


class InvalidJSONClient(LLMClient):
    async def complete(self, prompt: str) -> str:
        return "not json"


class EmptyPatchClient(LLMClient):
    async def complete(self, prompt: str) -> str:
        return (
            '{"target_file": "train.py", "rationale": "none", '
            '"proposed_change": "none", "unified_diff": "", "confidence": 0.1}'
        )


def valid_patch_json() -> str:
    return (
        '{"target_file": "train.py", '
        '"rationale": "Fix tensor shape.", '
        '"proposed_change": "Change 128 to 64.", '
        '"unified_diff": "--- train.py\\n+++ train.py\\n@@\\n'
        '-    classifier_expected_dim = 128\\n'
        '+    classifier_expected_dim = 64\\n", '
        '"confidence": 0.8}'
    )


def create_tensor_shape_repo(tmp_path: Path) -> tuple[Path, BenchmarkTask]:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "train.py").write_text(
        "import sys\n"
        "\n"
        "\n"
        "def main():\n"
        "    classifier_expected_dim = 128\n"
        "    if classifier_expected_dim == 128:\n"
        "        print(\n"
        "            \"RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)\",\n"
        "            file=sys.stderr,\n"
        "            flush=True,\n"
        "        )\n"
        "        sys.exit(1)\n"
        "    print(\"Verification succeeded after patch.\", flush=True)\n"
        "\n"
        "\n"
        "if __name__ == \"__main__\":\n"
        "    main()\n",
        encoding="utf-8",
    )
    task = BenchmarkTask(
        task_id="fake_repair_tensor_shape_001",
        task_name="Fake tensor shape task",
        category="runtime_repair",
        difficulty="easy",
        entry_command=f"{sys.executable} train.py",
        task_dir=str(tmp_path),
        repo_dir=str(repo_dir),
        expected_diagnosis_path=str(tmp_path / "expected_diagnosis.json"),
        requires=[],
    )
    return repo_dir, task


def create_parsed_error() -> ParsedError:
    return ParsedError(
        error_type="tensor_shape",
        summary="Tensor shape mismatch.",
        evidence=[
            "RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)"
        ],
    )


@pytest.mark.asyncio
async def test_llm_patch_planner_creates_patch_plan_from_mock_json(tmp_path) -> None:
    repo_dir, _ = create_tensor_shape_repo(tmp_path)
    parsed_error = create_parsed_error()
    failure_memory = FailureMemoryBuilder().from_parsed_error(parsed_error)

    plan = await LLMPatchPlanner(MockLLMClient()).create_plan(
        task_id="fake_repair_tensor_shape_001",
        parsed_error=parsed_error,
        failure_memory=failure_memory,
        repo_dir=str(repo_dir),
    )

    assert plan is not None
    assert plan.target_file == "train.py"
    assert plan.unified_diff
    assert plan.confidence >= 0.5


@pytest.mark.asyncio
async def test_llm_patch_planner_invalid_json_returns_none(tmp_path) -> None:
    repo_dir, _ = create_tensor_shape_repo(tmp_path)
    parsed_error = create_parsed_error()
    failure_memory = FailureMemoryBuilder().from_parsed_error(parsed_error)

    plan = await LLMPatchPlanner(InvalidJSONClient()).create_plan(
        task_id="fake_repair_tensor_shape_001",
        parsed_error=parsed_error,
        failure_memory=failure_memory,
        repo_dir=str(repo_dir),
    )

    assert plan is None


def test_llm_patch_planner_parses_pure_json_response() -> None:
    plan = LLMPatchPlanner()._parse_response(
        task_id="task_1",
        error_type="tensor_shape",
        raw_response=valid_patch_json(),
    )

    assert plan is not None
    assert plan.target_file == "train.py"


def test_llm_patch_planner_parses_fenced_json_response() -> None:
    plan = LLMPatchPlanner()._parse_response(
        task_id="task_1",
        error_type="tensor_shape",
        raw_response=f"```json\n{valid_patch_json()}\n```",
    )

    assert plan is not None
    assert plan.confidence == 0.8


def test_llm_patch_planner_parses_json_object_with_surrounding_text() -> None:
    plan = LLMPatchPlanner()._parse_response(
        task_id="task_1",
        error_type="tensor_shape",
        raw_response=f"Here is the plan:\n{valid_patch_json()}\nApply after review.",
    )

    assert plan is not None
    assert plan.unified_diff


def test_llm_patch_planner_invalid_response_returns_none() -> None:
    plan = LLMPatchPlanner()._parse_response(
        task_id="task_1",
        error_type="tensor_shape",
        raw_response="No JSON here.",
    )

    assert plan is None


@pytest.mark.asyncio
async def test_repair_runner_falls_back_to_rule_planner_when_llm_returns_none(tmp_path) -> None:
    _, task = create_tensor_shape_repo(tmp_path)
    event_bus = EventBus()
    policy = RepairPolicy(require_confirmation=True, approved=True)

    result = await RepairBenchmarkRunner(event_bus).run(
        task,
        policy=policy,
        use_llm_planner=True,
        llm_client=EmptyPatchClient(),
    )

    assert result.patch_plan_generated is True
    assert result.patch_applied is True
    assert result.verification_success is True
    assert result.score == 1.0
