import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.memory.failure_memory import FailureMemory
from scicodepilot.repair.patch_planner import PatchPlanner
from scicodepilot.tools.traceback_parser import ParsedError


def make_tensor_shape_error() -> ParsedError:
    return ParsedError(
        error_type="tensor_shape",
        summary=(
            "The program failed due to a tensor shape mismatch during tensor "
            "computation."
        ),
        evidence=[
            "RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)"
        ],
    )


def make_tensor_shape_memory(parsed_error: ParsedError) -> FailureMemory:
    return FailureMemory(
        error_type="tensor_shape",
        evidence=parsed_error.evidence,
        root_cause_hypothesis=(
            "The tensor feature dimension used in matrix multiplication is "
            "inconsistent with the expected input dimension of the downstream layer."
        ),
        repair_action=(
            "Inspect the tensor shape before the failing matrix multiplication and "
            "align the downstream layer input dimension with the actual upstream "
            "feature dimension."
        ),
    )


def make_memory(parsed_error: ParsedError) -> FailureMemory:
    return FailureMemory(
        error_type=parsed_error.error_type,
        evidence=parsed_error.evidence,
        root_cause_hypothesis="Root cause for test.",
        repair_action="Repair action for test.",
    )


def test_patch_planner_generates_tensor_shape_plan() -> None:
    repo_dir = "benchmark/tasks/repair_tensor_shape_001/repo"
    parsed_error = make_tensor_shape_error()
    failure_memory = make_tensor_shape_memory(parsed_error)

    plan = PatchPlanner().create_plan(
        task_id="repair_tensor_shape_001",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=failure_memory,
    )

    assert plan is not None
    assert plan.error_type == "tensor_shape"
    assert plan.target_file == "train.py"
    assert plan.suspected_line is not None
    assert "classifier_expected_dim" in plan.unified_diff
    assert "-    classifier_expected_dim = 128" in plan.unified_diff
    assert "+    classifier_expected_dim = 64" in plan.unified_diff
    assert 0.0 <= plan.confidence <= 1.0


def test_patch_planner_returns_none_for_unsupported_error_type() -> None:
    repo_dir = "benchmark/tasks/repair_tensor_shape_001/repo"
    parsed_error = ParsedError(
        error_type="missing_module",
        summary="The program failed because a required Python module is missing.",
        evidence=["ModuleNotFoundError: No module named 'example'"],
    )
    failure_memory = FailureMemory(
        error_type="missing_module",
        evidence=parsed_error.evidence,
        root_cause_hypothesis="A required module is missing.",
        repair_action="Install or align the required package.",
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_tensor_shape_001",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=failure_memory,
    )

    assert plan is None


def test_patch_planner_returns_none_for_missing_file() -> None:
    repo_dir = "benchmark/tasks/repair_missing_file_004/repo"
    parsed_error = ParsedError(
        error_type="missing_file",
        summary="The program failed because a required file is missing.",
        evidence=["FileNotFoundError"],
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_missing_file_004",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=make_memory(parsed_error),
    )

    assert plan is None


def test_patch_planner_generates_entrypoint_plan() -> None:
    repo_dir = "benchmark/tasks/repair_entrypoint_error_005/repo"
    parsed_error = ParsedError(
        error_type="entrypoint_error",
        summary="The program failed because the script entrypoint appears to be misspelled.",
        evidence=["NameError: name 'mainn' is not defined"],
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_entrypoint_error_005",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=make_memory(parsed_error),
    )

    assert plan is not None
    assert plan.error_type == "entrypoint_error"
    assert "-    mainn()" in plan.unified_diff
    assert "+    main()" in plan.unified_diff


def test_patch_planner_generates_label_shape_plan() -> None:
    repo_dir = "benchmark/tasks/repair_label_shape_006/repo"
    parsed_error = ParsedError(
        error_type="label_shape",
        summary="The program failed because the label batch shape does not match.",
        evidence=["Expected input batch_size (8) to match target batch_size (9)."],
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_label_shape_006",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=make_memory(parsed_error),
    )

    assert plan is not None
    assert plan.error_type == "label_shape"
    assert "-    labels = torch.randint(0, num_classes, (batch_size + 1,), device=device)" in plan.unified_diff
    assert "+    labels = torch.randint(0, num_classes, (batch_size,), device=device)" in plan.unified_diff


def test_patch_planner_generates_device_mismatch_plan() -> None:
    repo_dir = "benchmark/tasks/repair_device_mismatch_007/repo"
    parsed_error = ParsedError(
        error_type="device_mismatch",
        summary="The program failed because tensors were on incompatible devices.",
        evidence=["Expected all tensors to be on the same device"],
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_device_mismatch_007",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=make_memory(parsed_error),
    )

    assert plan is not None
    assert plan.error_type == "device_mismatch"
    assert '-    input_device = "cuda:0"' in plan.unified_diff
    assert '+    input_device = "cpu"' in plan.unified_diff


def test_patch_planner_generates_loss_input_plan() -> None:
    repo_dir = "benchmark/tasks/repair_loss_input_008/repo"
    parsed_error = ParsedError(
        error_type="loss_input_error",
        summary="The loss input or target preparation is incompatible.",
        evidence=["loss_input_error"],
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_loss_input_008",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=make_memory(parsed_error),
    )

    assert plan is not None
    assert plan.error_type == "loss_input_error"
    assert '-    target_kind = "probabilities"' in plan.unified_diff
    assert '+    target_kind = "class_indices"' in plan.unified_diff


def test_patch_planner_generates_collate_fn_plan() -> None:
    repo_dir = "benchmark/tasks/repair_collate_fn_009/repo"
    parsed_error = ParsedError(
        error_type="collate_fn_error",
        summary="The collate function produced a wrong batch structure.",
        evidence=["collate_fn_error"],
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_collate_fn_009",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=make_memory(parsed_error),
    )

    assert plan is not None
    assert plan.error_type == "collate_fn_error"
    assert '-    return {"features": xs, "labels": ys}' in plan.unified_diff
    assert '+    return {"x": xs, "y": ys}' in plan.unified_diff


def test_patch_planner_generates_config_key_plan() -> None:
    repo_dir = "benchmark/tasks/repair_config_key_010/repo"
    parsed_error = ParsedError(
        error_type="config_key_error",
        summary="The experiment configuration key does not match.",
        evidence=["config_key_error"],
    )

    plan = PatchPlanner().create_plan(
        task_id="repair_config_key_010",
        repo_dir=repo_dir,
        parsed_error=parsed_error,
        failure_memory=make_memory(parsed_error),
    )

    assert plan is not None
    assert plan.error_type == "config_key_error"
    assert '-        learning_rate = config["learningrate"]' in plan.unified_diff
    assert '+        learning_rate = config["learning_rate"]' in plan.unified_diff


def test_patch_planner_does_not_modify_file() -> None:
    repo_dir = Path("benchmark/tasks/repair_tensor_shape_001/repo")
    train_path = repo_dir / "train.py"
    original_content = train_path.read_text(encoding="utf-8")
    parsed_error = make_tensor_shape_error()
    failure_memory = make_tensor_shape_memory(parsed_error)

    PatchPlanner().create_plan(
        task_id="repair_tensor_shape_001",
        repo_dir=str(repo_dir),
        parsed_error=parsed_error,
        failure_memory=failure_memory,
    )

    updated_content = train_path.read_text(encoding="utf-8")
    assert updated_content == original_content
