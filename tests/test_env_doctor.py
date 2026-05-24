import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.env.env_doctor import EnvDoctor
from scicodepilot.memory.failure_memory import FailureMemoryBuilder
from scicodepilot.tools.traceback_parser import ParsedError


def build_plan(error_type: str, evidence: list[str]):
    parsed_error = ParsedError(
        error_type=error_type,
        summary=f"{error_type} summary",
        evidence=evidence,
    )
    failure_memory = FailureMemoryBuilder().from_parsed_error(parsed_error)
    return EnvDoctor().create_plan(
        task_id="task_1",
        parsed_error=parsed_error,
        failure_memory=failure_memory,
    )


def test_missing_module_generates_env_repair_plan_with_import_verification() -> None:
    plan = build_plan(
        "missing_module",
        ["ModuleNotFoundError: No module named 'missing_pkg'"],
    )

    assert plan is not None
    assert plan.task_id == "task_1"
    assert plan.issue_category == "dependency"
    assert plan.requires_user_action is True
    assert plan.verification_command == 'python -c "import missing_pkg"'
    assert any("missing dependency" in action for action in plan.suggested_actions)
    assert any("active conda environment" in action for action in plan.suggested_actions)
    assert any("Rerun the benchmark command" in action for action in plan.suggested_actions)


def test_missing_file_generates_env_repair_plan_with_missing_path() -> None:
    plan = build_plan(
        "missing_file",
        [
            "FileNotFoundError: [Errno 2] No such file or directory: "
            "'data/train.csv'"
        ],
    )

    assert plan is not None
    assert plan.issue_category == "data"
    assert plan.requires_user_action is True
    assert plan.verification_command is None
    assert "data/train.csv" in plan.summary
    assert any("data/train.csv" in action for action in plan.suggested_actions)
    assert any("dataset or config path" in action for action in plan.suggested_actions)


def test_source_code_errors_return_none() -> None:
    for error_type in ["tensor_shape", "dtype_mismatch", "entrypoint_error", "label_shape"]:
        assert build_plan(error_type, ["runtime evidence"]) is None
