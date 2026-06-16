from pathlib import Path
import re

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

        original_content = target_path.read_text(encoding="utf-8")
        updated_content = original_content

        if replacements:
            for old_line, new_line in replacements:
                if old_line not in updated_content:
                    return False

                updated_content = updated_content.replace(old_line, new_line, 1)
        else:
            patched_content = self._apply_single_file_unified_diff(
                original_content,
                patch_plan.unified_diff,
            )
            if patched_content is None:
                return False
            updated_content = patched_content

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

    def _apply_single_file_unified_diff(
        self,
        original_content: str,
        unified_diff: str,
    ) -> str | None:
        """Apply a simple single-file unified diff, including pure insertions."""
        original_lines = original_content.splitlines()
        keep_trailing_newline = original_content.endswith("\n")
        diff_lines = unified_diff.splitlines()
        output_lines: list[str] = []
        old_cursor = 0
        index = 0
        saw_hunk = False
        hunk_pattern = re.compile(r"@@ -(?P<old_start>\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")

        while index < len(diff_lines):
            diff_line = diff_lines[index]
            if diff_line.startswith(("--- ", "+++ ")):
                index += 1
                continue

            match = hunk_pattern.match(diff_line)
            if match is None:
                index += 1
                continue

            saw_hunk = True
            old_start = int(match.group("old_start")) - 1
            if old_start < old_cursor or old_start > len(original_lines):
                return None

            output_lines.extend(original_lines[old_cursor:old_start])
            old_cursor = old_start
            index += 1

            while index < len(diff_lines) and not diff_lines[index].startswith("@@"):
                line = diff_lines[index]
                if line.startswith(" "):
                    expected = line[1:]
                    if old_cursor >= len(original_lines) or original_lines[old_cursor] != expected:
                        return None
                    output_lines.append(expected)
                    old_cursor += 1
                elif line.startswith("-"):
                    expected = line[1:]
                    if old_cursor >= len(original_lines) or original_lines[old_cursor] != expected:
                        return None
                    old_cursor += 1
                elif line.startswith("+"):
                    output_lines.append(line[1:])
                elif line.startswith("\\"):
                    pass
                else:
                    return None
                index += 1

        if not saw_hunk:
            return None

        output_lines.extend(original_lines[old_cursor:])
        updated_content = "\n".join(output_lines)
        if keep_trailing_newline:
            updated_content += "\n"
        return updated_content
