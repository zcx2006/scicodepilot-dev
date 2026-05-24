import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.memory.failure_memory import FailureMemory, FailureMemoryBuilder
from scicodepilot.tools.traceback_parser import ParsedError


def build_memory(error_type: str) -> FailureMemory:
    parsed_error = ParsedError(
        error_type=error_type,
        summary="summary",
        evidence=["evidence line"],
    )
    return FailureMemoryBuilder().from_parsed_error(parsed_error)


def test_build_tensor_shape_memory() -> None:
    memory = build_memory("tensor_shape")

    assert memory.error_type == "tensor_shape"
    assert memory.root_cause_hypothesis
    assert memory.repair_action
    assert memory.evidence == ["evidence line"]


def test_build_device_mismatch_memory() -> None:
    memory = build_memory("device_mismatch")

    assert memory.error_type == "device_mismatch"
    assert "device placement" in memory.repair_action
    assert "same target device" in memory.repair_action


def test_build_dtype_mismatch_memory() -> None:
    memory = build_memory("dtype_mismatch")

    assert memory.error_type == "dtype_mismatch"
    assert memory.root_cause_hypothesis
    assert memory.repair_action


def test_build_loss_input_error_memory() -> None:
    memory = build_memory("loss_input_error")

    assert memory.error_type == "loss_input_error"
    assert "loss" in memory.root_cause_hypothesis
    assert "class indices" in memory.repair_action


def test_build_missing_module_memory() -> None:
    memory = build_memory("missing_module")

    assert memory.error_type == "missing_module"
    assert "install" in memory.repair_action
    assert "environment" in memory.repair_action


def test_build_missing_file_memory() -> None:
    memory = build_memory("missing_file")

    assert memory.error_type == "missing_file"
    assert "file path" in memory.root_cause_hypothesis
    assert "Verify" in memory.repair_action


def test_build_entrypoint_error_memory() -> None:
    memory = build_memory("entrypoint_error")

    assert memory.error_type == "entrypoint_error"
    assert "misspelled" in memory.root_cause_hypothesis
    assert "mainn" in memory.repair_action


def test_build_label_shape_memory() -> None:
    memory = build_memory("label_shape")

    assert memory.error_type == "label_shape"
    assert "batch size" in memory.root_cause_hypothesis
    assert "Align" in memory.repair_action


def test_build_collate_fn_error_memory() -> None:
    memory = build_memory("collate_fn_error")

    assert memory.error_type == "collate_fn_error"
    assert "batch structure" in memory.root_cause_hypothesis
    assert "collate function" in memory.repair_action


def test_build_config_key_error_memory() -> None:
    memory = build_memory("config_key_error")

    assert memory.error_type == "config_key_error"
    assert "configuration key" in memory.root_cause_hypothesis
    assert "learning_rate" in memory.repair_action


def test_build_unknown_memory_uses_fallback() -> None:
    memory = build_memory("unknown_custom_error")

    assert memory.error_type == "unknown_custom_error"
    assert "no specialized hypothesis" in memory.root_cause_hypothesis
