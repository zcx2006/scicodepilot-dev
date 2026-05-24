from dataclasses import dataclass

from pydantic import BaseModel


class ParsedError(BaseModel):
    """A small structured view of an error parsed from stderr."""

    error_type: str
    summary: str
    evidence: list[str]


@dataclass(frozen=True)
class ErrorRule:
    """One rule that maps stderr text patterns to a structured error type."""

    error_type: str
    patterns: tuple[str, ...]
    summary: str


# M4 uses a small rule table instead of one hard-coded if branch. New rules can
# be added here later for missing_file, path_error, permission_error, and more.
ERROR_RULES = (
    ErrorRule(
        error_type="tensor_shape",
        patterns=(
            "mat1 and mat2 shapes cannot be multiplied",
            "size mismatch",
        ),
        summary=(
            "The program failed due to a tensor shape mismatch during tensor "
            "computation."
        ),
    ),
    ErrorRule(
        error_type="device_mismatch",
        patterns=(
            "Expected all tensors to be on the same device",
            "found at least two devices",
        ),
        summary=(
            "The program failed because tensors were placed on incompatible "
            "devices."
        ),
    ),
    ErrorRule(
        error_type="loss_input_error",
        patterns=(
            "loss_input_error",
            "CrossEntropyLoss expected class index",
            "BCEWithLogitsLoss target",
        ),
        summary=(
            "The program failed because the loss input or target preparation is "
            "incompatible with the expected loss contract."
        ),
    ),
    ErrorRule(
        error_type="dtype_mismatch",
        patterns=(
            "expected scalar type",
            "mat1 and mat2 must have the same dtype",
            "have the same dtype",
            "Found dtype",
        ),
        summary=(
            "The program failed because tensors or operators used incompatible "
            "data types."
        ),
    ),
    ErrorRule(
        error_type="missing_module",
        patterns=(
            "ModuleNotFoundError",
            "No module named",
        ),
        summary=(
            "The program failed because a required Python module is not "
            "installed or not importable."
        ),
    ),
    ErrorRule(
        error_type="missing_file",
        patterns=(
            "FileNotFoundError",
            "No such file or directory",
        ),
        summary="The program failed because a required file is missing.",
    ),
    ErrorRule(
        error_type="entrypoint_error",
        patterns=(
            "NameError: name 'mainn'",
            "Did you mean: 'main'",
        ),
        summary=(
            "The program failed because the script entrypoint appears to be "
            "misspelled."
        ),
    ),
    ErrorRule(
        error_type="label_shape",
        patterns=(
            "Expected input batch_size",
            "target batch_size",
            "target size",
            "input size",
        ),
        summary=(
            "The program failed because the label batch shape does not match "
            "the model output batch shape."
        ),
    ),
    ErrorRule(
        error_type="collate_fn_error",
        patterns=(
            "collate_fn_error",
            "batch missing expected key",
            "default_collate",
        ),
        summary=(
            "The program failed because the DataLoader collate function produced "
            "a batch structure that does not match the training loop."
        ),
    ),
    ErrorRule(
        error_type="config_key_error",
        patterns=(
            "config_key_error",
            "missing experiment config key",
            "KeyError: 'learningrate'",
        ),
        summary=(
            "The program failed because the experiment configuration key used by "
            "the script does not match the available config fields."
        ),
    ),
)


class TracebackParser:
    """Minimal rule-table stderr parser for M4.

    This version recognizes a small set of common Python/PyTorch failures.
    Later stages can extend ERROR_RULES without changing the public parse API.
    """

    def parse(self, stderr_lines: list[str]) -> ParsedError | None:
        """Return a ParsedError for known stderr patterns, or None."""
        for line in stderr_lines:
            for rule in ERROR_RULES:
                if any(pattern in line for pattern in rule.patterns):
                    return ParsedError(
                        error_type=rule.error_type,
                        summary=rule.summary,
                        evidence=[line],
                    )

        return None
