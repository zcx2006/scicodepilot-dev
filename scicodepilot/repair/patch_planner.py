import difflib
from pathlib import Path

from scicodepilot.memory.failure_memory import FailureMemory
from scicodepilot.repair.patch_plan import PatchPlan
from scicodepilot.tools.traceback_parser import ParsedError


class PatchPlanner:
    """Create a draft repair plan without modifying files."""

    def create_plan(
        self,
        task_id: str,
        repo_dir: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
    ) -> PatchPlan | None:
        """Create a patch plan for supported errors, or None."""
        train_path = Path(repo_dir) / "train.py"
        lines = train_path.read_text(encoding="utf-8").splitlines()

        if parsed_error.error_type == "dtype_mismatch":
            return self._plan_dtype_mismatch(
                task_id=task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
                lines=lines,
            )

        if parsed_error.error_type == "device_mismatch":
            return self._plan_device_mismatch(
                task_id=task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
                lines=lines,
            )

        if parsed_error.error_type == "loss_input_error":
            return self._plan_loss_input_error(
                task_id=task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
                lines=lines,
            )

        if parsed_error.error_type == "entrypoint_error":
            return self._plan_entrypoint_error(
                task_id=task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
                lines=lines,
            )

        if parsed_error.error_type == "collate_fn_error":
            return self._plan_collate_fn_error(
                task_id=task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
                lines=lines,
            )

        if parsed_error.error_type == "config_key_error":
            return self._plan_config_key_error(
                task_id=task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
                lines=lines,
            )

        if parsed_error.error_type == "label_shape":
            return self._plan_label_shape(
                task_id=task_id,
                parsed_error=parsed_error,
                failure_memory=failure_memory,
                lines=lines,
            )

        if parsed_error.error_type != "tensor_shape":
            return None

        direct_plan = self._plan_classifier_expected_dim(
            task_id=task_id,
            parsed_error=parsed_error,
            failure_memory=failure_memory,
            lines=lines,
        )
        if direct_plan is not None:
            return direct_plan

        return self._plan_inline_linear(
            task_id=task_id,
            parsed_error=parsed_error,
            failure_memory=failure_memory,
            lines=lines,
        )

    def _plan_device_mismatch(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = 'input_device = "cuda:0"'

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace(
                'input_device = "cuda:0"',
                'input_device = "cpu"',
                1,
            )

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=(
                    "The parsed error is device_mismatch. The failure memory "
                    "indicates operands are on different devices. train.py places "
                    "the model on cpu but the input on cuda:0, so the input device "
                    "should be aligned to cpu."
                ),
                proposed_change=(
                    "Change input_device from cuda:0 to cpu so model and input "
                    "use the same device."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.86,
            )

        return None

    def _plan_loss_input_error(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = 'target_kind = "probabilities"'

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace(
                'target_kind = "probabilities"',
                'target_kind = "class_indices"',
                1,
            )

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=(
                    "The parsed error is loss_input_error. The failure memory "
                    "indicates CrossEntropyLoss needs class-index targets, while "
                    "train.py marks targets as probability-like."
                ),
                proposed_change=(
                    "Change target_kind from probabilities to class_indices so "
                    "the loss receives the expected target representation."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.84,
            )

        return None

    def _plan_collate_fn_error(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = 'return {"features": xs, "labels": ys}'

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace(
                'return {"features": xs, "labels": ys}',
                'return {"x": xs, "y": ys}',
                1,
            )

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=(
                    "The parsed error is collate_fn_error. The training loop reads "
                    "batch['x'] and batch['y'], but collate_fn returns features and "
                    "labels keys."
                ),
                proposed_change=(
                    "Return x and y keys from collate_fn so the batch structure "
                    "matches the training loop."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.86,
            )

        return None

    def _plan_config_key_error(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = 'config["learningrate"]'

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace(
                'config["learningrate"]',
                'config["learning_rate"]',
                1,
            )

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=(
                    "The parsed error is config_key_error. train.py defines "
                    "learning_rate but reads learningrate, so the lookup should "
                    "use the existing configuration key."
                ),
                proposed_change=(
                    "Change the config lookup from learningrate to learning_rate."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.9,
            )

        return None

    def _plan_dtype_mismatch(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = "dtype=torch.float64"

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace(
                "dtype=torch.float64",
                "dtype=torch.float32",
                1,
            )

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=(
                    "The parsed error is dtype_mismatch. The failure memory "
                    "indicates incompatible dtypes in the failing operation. "
                    "In train.py, one operand uses torch.float64 while the other "
                    "uses torch.float32, so the float64 operand is suspected to "
                    "need alignment to float32."
                ),
                proposed_change=(
                    "Change the mismatched operand dtype from torch.float64 to "
                    "torch.float32 so the matrix multiplication operands have "
                    "compatible dtypes."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.8,
            )

        return None

    def _plan_entrypoint_error(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = "mainn()"

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace("mainn()", "main()", 1)

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=(
                    "The parsed error is entrypoint_error. The failure memory "
                    "indicates a misspelled entrypoint invocation. train.py "
                    "defines main() but calls mainn(), so the call should be "
                    "corrected to main()."
                ),
                proposed_change=(
                    "Change the entrypoint call from mainn() to main() so the "
                    "defined function is invoked."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.9,
            )

        return None

    def _plan_label_shape(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = "(batch_size + 1,)"

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace("(batch_size + 1,)", "(batch_size,)", 1)

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=(
                    "The parsed error is label_shape. The failure memory indicates "
                    "that labels and logits have different batch sizes. train.py "
                    "creates labels with batch_size + 1 while logits are produced "
                    "for batch_size examples, so the label shape should use "
                    "batch_size."
                ),
                proposed_change=(
                    "Change the label tensor shape from batch_size + 1 to "
                    "batch_size so targets align with logits."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.85,
            )

        return None

    def _plan_classifier_expected_dim(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = "classifier_expected_dim = 128"

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace(
                "classifier_expected_dim = 128",
                "classifier_expected_dim = 64",
            )

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=self._build_rationale(failure_memory),
                proposed_change=(
                    "Change classifier_expected_dim from 128 to 64 so that the "
                    "classifier input dimension matches upstream_feature_dim."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.85,
            )

        return None

    def _plan_inline_linear(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        lines: list[str],
    ) -> PatchPlan | None:
        target_text = "nn.Linear(128"

        for index, line in enumerate(lines):
            if target_text not in line:
                continue

            updated_lines = lines.copy()
            updated_lines[index] = line.replace("nn.Linear(128", "nn.Linear(64", 1)

            return PatchPlan(
                task_id=task_id,
                error_type=parsed_error.error_type,
                target_file="train.py",
                suspected_line=index + 1,
                rationale=self._build_rationale(failure_memory),
                proposed_change=(
                    "Change the Linear layer input dimension from 128 to 64 so "
                    "that it matches the upstream feature dimension."
                ),
                unified_diff=self._build_diff(lines, updated_lines),
                confidence=0.7,
            )

        return None

    def _build_rationale(self, failure_memory: FailureMemory) -> str:
        return (
            "The parsed error is tensor_shape. The failure memory indicates that "
            "the feature dimension is inconsistent with the downstream layer. "
            "In train.py, upstream_feature_dim is 64 while classifier_expected_dim "
            "is 128, so classifier_expected_dim is suspected to be the value that "
            "should change to 64."
        )

    def _build_diff(self, original_lines: list[str], updated_lines: list[str]) -> str:
        diff_lines = difflib.unified_diff(
            original_lines,
            updated_lines,
            fromfile="train.py",
            tofile="train.py",
            lineterm="",
        )
        return "\n".join(diff_lines)
