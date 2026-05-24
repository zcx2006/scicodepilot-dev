from pathlib import Path

from scicodepilot.repair.patch_plan import PatchPlan
from scicodepilot.review.patch_review import PatchReview


class PatchSafetyReviewer:
    """Rule-based static safety review for patch plans."""

    blocked_path_parts = {"benchmark", "reference", "outputs", "tests", ".git"}
    blocked_file_names = {"pyproject.toml", "requirements.txt"}
    blocked_diff_terms = (
        "rm -rf",
        "sudo",
        "curl | sh",
        "wget | bash",
        "pip install",
        "conda install",
        "os.system",
        "subprocess",
        "eval(",
        "exec(",
    )

    def review(self, patch_plan: PatchPlan, workspace_repo_dir: str) -> PatchReview:
        reasons: list[str] = []
        warnings: list[str] = []

        if not patch_plan.unified_diff.strip():
            reasons.append("Patch unified_diff is empty.")

        self._review_target_path(patch_plan, workspace_repo_dir, reasons)
        self._review_target_area(patch_plan.target_file, reasons)
        self._review_diff_content(patch_plan.unified_diff, reasons)
        self._review_single_file_diff(patch_plan.unified_diff, reasons)
        self._review_error_alignment(patch_plan, warnings)

        blocked = bool(reasons)
        risk_level = "high" if blocked else "medium" if warnings else "low"
        approved = not blocked and risk_level in {"low", "medium"}

        if approved and not warnings:
            reasons.append("No blocking safety risks detected.")

        return PatchReview(
            task_id=patch_plan.task_id,
            error_type=patch_plan.error_type,
            target_file=patch_plan.target_file,
            approved=approved,
            blocked=blocked,
            risk_level=risk_level,
            reasons=reasons,
            warnings=warnings,
        )

    def _review_target_path(
        self,
        patch_plan: PatchPlan,
        workspace_repo_dir: str,
        reasons: list[str],
    ) -> None:
        target_path = Path(patch_plan.target_file)
        if target_path.is_absolute():
            reasons.append("Patch target_file must be a relative path.")
            return

        if ".." in target_path.parts:
            reasons.append("Patch target_file must not contain path traversal.")
            return

        workspace_path = Path(workspace_repo_dir).resolve()
        resolved_target = (workspace_path / target_path).resolve()
        if not resolved_target.is_relative_to(workspace_path):
            reasons.append("Patch target_file resolves outside the workspace repo.")

    def _review_target_area(self, target_file: str, reasons: list[str]) -> None:
        target_path = Path(target_file)
        if any(part in self.blocked_path_parts for part in target_path.parts):
            reasons.append(f"Patch target_file points to a blocked area: {target_file}.")
        if target_path.name in self.blocked_file_names:
            reasons.append(f"Patch target_file is blocked: {target_path.name}.")

    def _review_diff_content(self, unified_diff: str, reasons: list[str]) -> None:
        diff_text = unified_diff.lower()
        for term in self.blocked_diff_terms:
            if term in diff_text:
                reasons.append(f"Patch diff contains blocked content: {term}.")

    def _review_single_file_diff(self, unified_diff: str, reasons: list[str]) -> None:
        old_headers = [
            line for line in unified_diff.splitlines() if line.startswith("--- ")
        ]
        new_headers = [
            line for line in unified_diff.splitlines() if line.startswith("+++ ")
        ]
        if len(old_headers) > 1 or len(new_headers) > 1:
            reasons.append("Patch diff appears to modify multiple files.")

    def _review_error_alignment(
        self,
        patch_plan: PatchPlan,
        warnings: list[str],
    ) -> None:
        text = f"{patch_plan.proposed_change}\n{patch_plan.unified_diff}".lower()
        alignment_checks = {
            "tensor_shape": ("classifier_expected_dim", "64", "128"),
            "device_mismatch": ("device", "cpu", "cuda"),
            "dtype_mismatch": ("float32", "float64", "dtype"),
            "loss_input_error": ("loss", "target", "class_indices"),
            "entrypoint_error": ("main", "mainn"),
            "label_shape": ("batch_size", "labels"),
            "collate_fn_error": ("collate", "batch", '"x"', '"y"'),
            "config_key_error": ("config", "learning_rate", "learningrate"),
        }
        tokens = alignment_checks.get(patch_plan.error_type)
        if tokens is None:
            return

        if not any(token in text for token in tokens):
            warnings.append(
                "Patch content has weak alignment with the parsed error type."
            )
