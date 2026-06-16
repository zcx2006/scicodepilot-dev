from pydantic import BaseModel

from scicodepilot.tools.traceback_parser import ParsedError


class FailureMemory(BaseModel):
    """Structured memory derived from a parsed command failure."""

    error_type: str
    evidence: list[str]
    root_cause_hypothesis: str
    repair_action: str


class FailureMemoryBuilder:
    """Build reusable failure memory from parsed error information."""

    def from_parsed_error(self, parsed_error: ParsedError) -> FailureMemory:
        """Create specialized memory when possible, otherwise use a safe fallback."""
        if (
            parsed_error.error_type == "external_assertion_failure"
            and parsed_error.target_symbol == "unified_strdate"
        ):
            return FailureMemory(
                error_type=parsed_error.error_type,
                evidence=parsed_error.evidence,
                root_cause_hypothesis=(
                    "The external verification command asserted that "
                    "unified_strdate('not-a-date') should return None, but the "
                    "assertion failed. The date parser leaves upload_date as "
                    "None for invalid date strings, but the implementation "
                    "converts None with compat_str, producing the string 'None' "
                    "instead of returning None."
                ),
                repair_action=(
                    "Guard the final compat_str(upload_date) conversion and "
                    "return a value only when upload_date is not None."
                ),
            )

        memory_templates = {
            "tensor_shape": (
                "The tensor feature dimension used in matrix multiplication is "
                "inconsistent with the expected input dimension of the downstream "
                "layer.",
                "Inspect the tensor shape before the failing matrix multiplication "
                "and align the downstream layer input dimension with the actual "
                "upstream feature dimension.",
            ),
            "device_mismatch": (
                "Some tensors or model parameters are located on different "
                "devices, such as CPU and CUDA, during the same computation.",
                "Inspect model and tensor device placement, then move all operands "
                "involved in the failing computation to the same target device.",
            ),
            "loss_input_error": (
                "The loss function receives a target or input representation that "
                "does not match the expected loss contract.",
                "Inspect the loss inputs and prepare targets as class indices or "
                "compatible tensors before computing the loss.",
            ),
            "dtype_mismatch": (
                "The failing operation received tensors with incompatible dtypes, "
                "causing the operator to reject the computation.",
                "Inspect the dtype of the tensors involved in the failing operation "
                "and convert them to compatible dtypes before the computation.",
            ),
            "missing_module": (
                "The Python environment does not currently expose a module required "
                "by the target script.",
                "Check whether the dependency is missing, incorrectly named, or "
                "installed in a different environment, then install or align the "
                "required package.",
            ),
            "missing_file": (
                "The script references a file path that is missing from the current "
                "benchmark repo or working directory.",
                "Verify the required dataset or config path, then provide the "
                "missing file or correct the path configuration before rerunning.",
            ),
            "entrypoint_error": (
                "The script entrypoint call is likely misspelled, so Python cannot "
                "find the intended function at startup.",
                "Inspect the entrypoint invocation and replace the misspelled "
                "function name mainn with the defined main function.",
            ),
            "label_shape": (
                "The label tensor batch size is inconsistent with the model output "
                "batch size expected by the loss function.",
                "Align the label batch size with the logits batch size before "
                "computing the loss.",
            ),
            "collate_fn_error": (
                "The collate function returns a batch structure whose keys or "
                "shape do not match the training loop expectation.",
                "Align the collate function output with the batch structure read "
                "by the training loop.",
            ),
            "config_key_error": (
                "The script reads a configuration key that does not exist in the "
                "experiment configuration.",
                "Use the existing configuration key name, such as learning_rate, "
                "or add explicit key validation before reading the config.",
            ),
            "external_assertion_failure": (
                "External AssertionError triggered while running the "
                "user-provided command. The command reached an assert statement "
                "in application code. When the assertion checks that a value is "
                "bool, the observed control path can produce None if a requested "
                "configuration key is absent.",
                "Inspect the assignment immediately before the assertion. If a "
                "dict .get(...) call can return None and the surrounding function "
                "should emit no CLI arguments for missing options, add a "
                "conservative None guard before the bool assertion.",
            ),
            "external_type_error": (
                "External TypeError triggered because a non-string input reached "
                "string/regex processing. str_to_int accepts an int input, but "
                "the implementation only handles None specially and then passes "
                "int_str into re.sub, which expects a string or bytes-like object.",
                "Guard non-string inputs before regex normalization. If the input "
                "is not compat_str, return it unchanged.",
            ),
            "external_env_failure": (
                "The external command failed before reaching the target bug "
                "because the project depends on a standard-library module that "
                "is unavailable in the active Python interpreter.",
                "Use a compatible Python interpreter for this external case, "
                "such as Python 3.11 for older youtube-dl revisions that import "
                "the removed pipes module. Do not auto-install or modify the "
                "environment from the repair flow.",
            ),
        }

        template = memory_templates.get(parsed_error.error_type)
        if template is not None:
            root_cause_hypothesis, repair_action = template
            return FailureMemory(
                error_type=parsed_error.error_type,
                evidence=parsed_error.evidence,
                root_cause_hypothesis=root_cause_hypothesis,
                repair_action=repair_action,
            )

        return FailureMemory(
            error_type=parsed_error.error_type,
            evidence=parsed_error.evidence,
            root_cause_hypothesis=(
                "The command failed, but the current rule-based memory builder "
                "has no specialized hypothesis for this error type."
            ),
            repair_action=(
                "Inspect the stderr evidence manually and extend the "
                "failure-memory rules if this error type should be supported."
            ),
        )
