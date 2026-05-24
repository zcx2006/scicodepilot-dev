import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.tools.traceback_parser import TracebackParser


def test_parse_tensor_shape_error() -> None:
    line = "RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)"

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "tensor_shape"
    assert "tensor shape mismatch" in parsed_error.summary
    assert parsed_error.evidence == [line]


def test_parse_device_mismatch_error() -> None:
    line = (
        "RuntimeError: Expected all tensors to be on the same device, but found "
        "at least two devices, cuda:0 and cpu!"
    )

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "device_mismatch"


def test_parse_loss_input_error() -> None:
    line = (
        "ValueError: loss_input_error: CrossEntropyLoss expected class index "
        "targets, but received probability-like targets."
    )

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "loss_input_error"


def test_parse_dtype_mismatch_error() -> None:
    line = "RuntimeError: mat1 and mat2 must have the same dtype, but got Float and Half"

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "dtype_mismatch"


def test_parse_missing_module_error() -> None:
    line = "ModuleNotFoundError: No module named 'torchvision'"

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "missing_module"


def test_parse_missing_file_error() -> None:
    line = "FileNotFoundError: [Errno 2] No such file or directory: 'data/train.csv'"

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "missing_file"


def test_parse_entrypoint_error() -> None:
    line = "NameError: name 'mainn' is not defined. Did you mean: 'main'?"

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "entrypoint_error"


def test_parse_label_shape_error() -> None:
    line = "ValueError: Expected input batch_size (8) to match target batch_size (9)."

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "label_shape"


def test_parse_collate_fn_error() -> None:
    line = "KeyError: collate_fn_error: batch missing expected key 'x'"

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "collate_fn_error"


def test_parse_config_key_error() -> None:
    line = "KeyError: config_key_error: missing experiment config key 'learningrate'"

    parsed_error = TracebackParser().parse([line])

    assert parsed_error is not None
    assert parsed_error.error_type == "config_key_error"


def test_parse_unknown_error_returns_none() -> None:
    parsed_error = TracebackParser().parse(
        ["RuntimeError: something unexpected happened"]
    )

    assert parsed_error is None
