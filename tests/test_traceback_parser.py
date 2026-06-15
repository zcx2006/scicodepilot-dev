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


def test_parse_external_assertion_error_traceback() -> None:
    stderr_lines = [
        "Traceback (most recent call last):",
        '  File "<string>", line 1, in <module>',
        '  File "/tmp/workspace/youtube_dl/utils.py", line 2133, in cli_bool_option',
        "    assert isinstance(param, bool)",
        "AssertionError",
    ]

    parsed_error = TracebackParser().parse(stderr_lines)

    assert parsed_error is not None
    assert parsed_error.error_type == "external_assertion_failure"
    assert parsed_error.exception_type == "AssertionError"
    assert parsed_error.assertion_expr is not None
    assert "assert isinstance(param, bool)" in parsed_error.assertion_expr
    assert parsed_error.function_name == "cli_bool_option"


def test_parse_external_type_error_traceback() -> None:
    stderr_lines = [
        "Traceback (most recent call last):",
        '  File "<string>", line 1, in <module>',
        '  File "/tmp/workspace/sample.py", line 6, in str_to_int',
        "    int_str = re.sub(r'[,\\.]+', '', int_str)",
        '  File "/usr/lib/python3.11/re/__init__.py", line 185, in sub',
        "TypeError: expected string or bytes-like object, got 'int'",
    ]

    parsed_error = TracebackParser().parse(stderr_lines)

    assert parsed_error is not None
    assert parsed_error.error_type == "external_type_error"
    assert parsed_error.exception_type == "TypeError"
    assert parsed_error.error_message is not None
    assert "expected string or bytes-like object" in parsed_error.error_message
    assert parsed_error.function_name == "str_to_int"


def test_parse_command_level_assertion_error() -> None:
    command = (
        "python -c \"from sample import unified_strdate; "
        "assert unified_strdate('not-a-date') is None\""
    )
    stderr_lines = [
        "Traceback (most recent call last):",
        '  File "<string>", line 1, in <module>',
        "AssertionError",
    ]

    parsed_error = TracebackParser().parse(stderr_lines, command=command)

    assert parsed_error is not None
    assert parsed_error.error_type == "external_assertion_failure"
    assert parsed_error.assertion_location == "command"
    assert parsed_error.target_symbol == "unified_strdate"
    assert parsed_error.expected_value == "None"


def test_parse_external_pipes_env_failure() -> None:
    parsed_error = TracebackParser().parse(
        ["ModuleNotFoundError: No module named 'pipes'"]
    )

    assert parsed_error is not None
    assert parsed_error.error_type == "external_env_failure"
    assert parsed_error.exception_type == "ModuleNotFoundError"
