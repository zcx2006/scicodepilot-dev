import json
import re
from pathlib import Path
from typing import Any

from scicodepilot.llm.llm_client import DisabledLLMClient, LLMClient
from scicodepilot.llm.prompt_templates import build_patch_prompt
from scicodepilot.memory.failure_memory import FailureMemory
from scicodepilot.repair.patch_plan import PatchPlan
from scicodepilot.tools.traceback_parser import ParsedError


class LLMPatchPlanner:
    """Optional adapter that turns LLM JSON into a PatchPlan."""

    def __init__(
        self,
        client: LLMClient | None = None,
        minimum_confidence: float = 0.5,
    ) -> None:
        self.client = client or DisabledLLMClient()
        self.minimum_confidence = minimum_confidence

    async def create_plan(
        self,
        task_id: str,
        parsed_error: ParsedError,
        failure_memory: FailureMemory,
        repo_dir: str,
    ) -> PatchPlan | None:
        target_file = "train.py"
        source_path = Path(repo_dir) / target_file
        if not source_path.exists():
            return None

        source_code = source_path.read_text(encoding="utf-8")
        prompt = build_patch_prompt(
            task_id=task_id,
            parsed_error=parsed_error,
            failure_memory=failure_memory,
            source_code=source_code,
            target_file=target_file,
        )
        raw_response = await self.client.complete(prompt)
        return self._parse_response(
            task_id=task_id,
            error_type=parsed_error.error_type,
            raw_response=raw_response,
        )

    def _parse_response(
        self,
        task_id: str,
        error_type: str,
        raw_response: str,
    ) -> PatchPlan | None:
        json_text = self._extract_json_text(raw_response)
        if json_text is None:
            return None

        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None

        required_fields = {
            "target_file",
            "rationale",
            "proposed_change",
            "unified_diff",
            "confidence",
        }
        if not required_fields.issubset(payload):
            return None

        target_file = payload["target_file"]
        rationale = payload["rationale"]
        proposed_change = payload["proposed_change"]
        unified_diff = payload["unified_diff"]
        confidence = self._coerce_confidence(payload["confidence"])

        if (
            not isinstance(target_file, str)
            or target_file != "train.py"
            or not isinstance(rationale, str)
            or not isinstance(proposed_change, str)
            or not isinstance(unified_diff, str)
            or not unified_diff.strip()
            or confidence is None
            or confidence < self.minimum_confidence
        ):
            return None

        return PatchPlan(
            task_id=task_id,
            error_type=error_type,
            target_file=target_file,
            suspected_line=None,
            rationale=rationale,
            proposed_change=proposed_change,
            unified_diff=unified_diff,
            confidence=confidence,
        )

    def _coerce_confidence(self, value: Any) -> float | None:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return None
        if confidence < 0.0 or confidence > 1.0:
            return None
        return confidence

    def _extract_json_text(self, raw_response: str) -> str | None:
        text = raw_response.strip()
        if not text:
            return None

        if self._looks_like_json_object(text):
            return text

        fence_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fence_match:
            return fence_match.group(1).strip()

        return self._extract_first_json_object(text)

    def _looks_like_json_object(self, text: str) -> bool:
        return text.startswith("{") and text.endswith("}")

    def _extract_first_json_object(self, text: str) -> str | None:
        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]

        return None
