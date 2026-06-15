import re
from dataclasses import dataclass

from pydantic import BaseModel


class ParsedError(BaseModel):
    """A small structured view of an error parsed from stderr."""

    error_type: str
    summary: str
    evidence: list[str]
    exception_type: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    function_name: str | None = None
    assertion_expr: str | None = None
    command: str | None = None
    stderr_evidence: list[str] | None = None


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
        assertion_error = self._parse_external_assertion_error(stderr_lines)
        if assertion_error is not None:
            return assertion_error

        for line in stderr_lines:
            for rule in ERROR_RULES:
                if any(pattern in line for pattern in rule.patterns):
                    return ParsedError(
                        error_type=rule.error_type,
                        summary=rule.summary,
                        evidence=[line],
                    )

        return None

    def _parse_external_assertion_error(
        self,
        stderr_lines: list[str],
    ) -> ParsedError | None:
        if not any("AssertionError" in line for line in stderr_lines):
            return None

        frame_pattern = re.compile(
            r'^\s*File "(?P<file>.+?)", line (?P<line>\d+), in (?P<func>[^\s]+)'
        )
        frames: list[tuple[str, int, str, int]] = []
        for index, line in enumerate(stderr_lines):
            match = frame_pattern.match(line)
            if match is None:
                continue
            frames.append(
                (
                    match.group("file"),
                    int(match.group("line")),
                    match.group("func"),
                    index,
                )
            )

        if not frames:
            return None

        file_path, line_number, function_name, frame_index = frames[-1]
        assertion_expr = self._find_assertion_expr(stderr_lines, frame_index)
        evidence = self._assertion_evidence(stderr_lines, assertion_expr)

        return ParsedError(
            error_type="external_assertion_failure",
            summary=(
                "External AssertionError triggered while running the "
                "user-provided command."
            ),
            evidence=evidence,
            exception_type="AssertionError",
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            assertion_expr=assertion_expr,
            stderr_evidence=evidence,
        )

    def _find_assertion_expr(
        self,
        stderr_lines: list[str],
        frame_index: int,
    ) -> str | None:
        for line in stderr_lines[frame_index + 1 :]:
            stripped = line.strip()
            if stripped.startswith('File "'):
                return None
            if stripped.startswith("assert "):
                return stripped
        return None

    def _assertion_evidence(
        self,
        stderr_lines: list[str],
        assertion_expr: str | None,
    ) -> list[str]:
        evidence: list[str] = []
        if assertion_expr:
            evidence.append(assertion_expr)
        evidence.extend(line.strip() for line in stderr_lines if "AssertionError" in line)
        return evidence or ["AssertionError"]
