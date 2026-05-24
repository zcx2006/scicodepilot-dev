from pathlib import Path

from scicodepilot.repair.patch_plan import PatchPlan


class PatchApplier:
    """Apply a minimal single-file text replacement patch.

    This is the M8 safety-first applier. It only supports simple old/new line
    replacements from PatchPlan.unified_diff. It is not a general patch engine,
    does not call shell patch tools, and does not use git apply.
    """

    def apply(self, repo_dir: str, patch_plan: PatchPlan) -> bool:
        target_path = Path(repo_dir) / patch_plan.target_file
        if not target_path.exists():
            return False

        replacements = self._extract_replacements(patch_plan.unified_diff)
        if not replacements:
            return False

        original_content = target_path.read_text(encoding="utf-8")
        updated_content = original_content

        for old_line, new_line in replacements:
            if old_line not in updated_content:
                return False

            updated_content = updated_content.replace(old_line, new_line, 1)

        target_path.write_text(updated_content, encoding="utf-8")
        return True

    def _extract_replacements(self, unified_diff: str) -> list[tuple[str, str]]:
        """Extract simple removed/added line pairs from a unified diff."""
        removed_lines: list[str] = []
        added_lines: list[str] = []

        for diff_line in unified_diff.splitlines():
            if (
                diff_line.startswith("---")
                or diff_line.startswith("+++")
                or diff_line.startswith("@@")
            ):
                continue

            if diff_line.startswith("-"):
                removed_lines.append(diff_line[1:])
            elif diff_line.startswith("+"):
                added_lines.append(diff_line[1:])

        if len(removed_lines) != len(added_lines):
            return []

        return list(zip(removed_lines, added_lines))
