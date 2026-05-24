import re

from scicodepilot.env.env_repair_plan import EnvRepairPlan
from scicodepilot.memory.failure_memory import FailureMemory
from scicodepilot.tools.traceback_parser import ParsedError


class EnvDoctor:
    """Create repair plans for dependency, environment, and data failures."""

    _MODULE_PATTERN = re.compile(r"No module named ['\"]([^'\"]+)['\"]")
    _FILE_PATTERN = re.compile(
        r"(?:No such file or directory|cannot find the file)[^'\"]*['\"]([^'\"]+)['\"]"
    )

    def create_plan(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
    ) -> EnvRepairPlan | None:
        """Return a structured non-source repair plan for supported errors."""
        if parsed_error.error_type == "missing_module":
            return self._create_missing_module_plan(task_id, parsed_error)

        if parsed_error.error_type == "missing_file":
            return self._create_missing_file_plan(task_id, parsed_error)

        return None

    def _create_missing_module_plan(
        self,
        task_id: str,
        parsed_error: ParsedError,
    ) -> EnvRepairPlan:
        module_name = self._extract_module_name(parsed_error.evidence)
        suggested_actions = [
            "Check requirements.txt, pyproject.toml, or README for the missing dependency.",
            "Install the dependency inside the active conda environment.",
        ]
        verification_command = None
        if module_name:
            verification_command = f'python -c "import {module_name}"'
            suggested_actions.append(f"Verify the import with {verification_command}.")
        else:
            suggested_actions.append(
                'Verify the import with python -c "import <module_name>" once the module name is known.'
            )
        suggested_actions.append("Rerun the benchmark command.")

        return EnvRepairPlan(
            task_id=task_id,
            error_type=parsed_error.error_type,
            issue_category="dependency",
            summary=(
                f"Missing Python module: {module_name}."
                if module_name
                else parsed_error.summary
            ),
            evidence=parsed_error.evidence,
            suggested_actions=suggested_actions,
            verification_command=verification_command,
            confidence=0.9 if module_name else 0.75,
            requires_user_action=True,
        )

    def _create_missing_file_plan(
        self,
        task_id: str,
        parsed_error: ParsedError,
    ) -> EnvRepairPlan:
        missing_path = self._extract_file_path(parsed_error.evidence)
        suggested_actions = [
            (
                f"Check whether the required file path exists: {missing_path}."
                if missing_path
                else "Check whether the required file path exists."
            ),
            "Verify the dataset or config path used by the benchmark.",
            "Download or place the required dataset/config file in the expected location.",
            "Rerun the benchmark command.",
        ]

        return EnvRepairPlan(
            task_id=task_id,
            error_type=parsed_error.error_type,
            issue_category="data",
            summary=(
                f"Missing required file: {missing_path}."
                if missing_path
                else parsed_error.summary
            ),
            evidence=parsed_error.evidence,
            suggested_actions=suggested_actions,
            verification_command=None,
            confidence=0.9 if missing_path else 0.75,
            requires_user_action=True,
        )

    def _extract_module_name(self, evidence: list[str]) -> str | None:
        for line in evidence:
            match = self._MODULE_PATTERN.search(line)
            if match:
                return match.group(1)
        return None

    def _extract_file_path(self, evidence: list[str]) -> str | None:
        for line in evidence:
            match = self._FILE_PATTERN.search(line)
            if match:
                return match.group(1)
        return None
