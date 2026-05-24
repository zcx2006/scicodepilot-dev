import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Minimal async completion interface used by LLMPatchPlanner."""

    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Return a raw model completion for a prompt."""


class DisabledLLMClient(LLMClient):
    """Client used when LLM planning is not configured."""

    async def complete(self, prompt: str) -> str:
        return ""


class MockLLMClient(LLMClient):
    """Deterministic test client that returns small JSON patch plans."""

    async def complete(self, prompt: str) -> str:
        if "error_type: tensor_shape" in prompt and "classifier_expected_dim = 128" in prompt:
            return self._json_response(
                rationale="The classifier input dimension should match the upstream feature dimension.",
                proposed_change="Change classifier_expected_dim from 128 to 64.",
                unified_diff=(
                    "--- train.py\n"
                    "+++ train.py\n"
                    "@@\n"
                    "-    classifier_expected_dim = 128\n"
                    "+    classifier_expected_dim = 64\n"
                ),
                confidence=0.85,
            )

        if "error_type: dtype_mismatch" in prompt and "dtype=torch.float64" in prompt:
            return self._json_response(
                rationale="The matrix multiplication operands should use matching dtypes.",
                proposed_change="Change the float64 tensor to float32.",
                unified_diff=(
                    "--- train.py\n"
                    "+++ train.py\n"
                    "@@\n"
                    "-    w = torch.randn(4, 4, dtype=torch.float64)\n"
                    "+    w = torch.randn(4, 4, dtype=torch.float32)\n"
                ),
                confidence=0.82,
            )

        if "error_type: entrypoint_error" in prompt and "mainn()" in prompt:
            return self._json_response(
                rationale="The script calls a misspelled entrypoint.",
                proposed_change="Change mainn() to main().",
                unified_diff=(
                    "--- train.py\n"
                    "+++ train.py\n"
                    "@@\n"
                    "-    mainn()\n"
                    "+    main()\n"
                ),
                confidence=0.9,
            )

        if "error_type: label_shape" in prompt and "batch_size + 1" in prompt:
            return self._json_response(
                rationale="The label tensor batch size should match the logits batch size.",
                proposed_change="Use batch_size instead of batch_size + 1 for labels.",
                unified_diff=(
                    "--- train.py\n"
                    "+++ train.py\n"
                    "@@\n"
                    "-    labels = torch.randint(0, num_classes, (batch_size + 1,), device=device)\n"
                    "+    labels = torch.randint(0, num_classes, (batch_size,), device=device)\n"
                ),
                confidence=0.84,
            )

        return self._json_response(
            rationale="No source-code patch should be proposed by the mock client.",
            proposed_change="No patch.",
            unified_diff="",
            confidence=0.1,
        )

    def _json_response(
        self,
        rationale: str,
        proposed_change: str,
        unified_diff: str,
        confidence: float,
    ) -> str:
        return json.dumps(
            {
                "target_file": "train.py",
                "rationale": rationale,
                "proposed_change": proposed_change,
                "unified_diff": unified_diff,
                "confidence": confidence,
            },
            sort_keys=True,
        )


class _JSONRestLLMClient(LLMClient):
    """Small urllib-based JSON REST client used by provider adapters."""

    timeout_seconds = 30

    async def _post_json(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict,
    ) -> dict:
        import asyncio

        return await asyncio.to_thread(
            self._post_json_sync,
            url,
            headers,
            payload,
        )

    def _post_json_sync(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict,
    ) -> dict:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=url,
            data=body,
            headers={
                "Content-Type": "application/json",
                **headers,
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
        return json.loads(response_body)


class DeepSeekLLMClient(_JSONRestLLMClient):
    """DeepSeek chat-completions client using the OpenAI-compatible REST API."""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def complete(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful code repair planner. Output JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
        }
        data = await self._post_json(
            url=f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            payload=payload,
        )
        return data["choices"][0]["message"]["content"]


class GeminiLLMClient(_JSONRestLLMClient):
    """Gemini generateContent REST client."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
    ) -> None:
        self.api_key = api_key
        self.model = model

    async def complete(self, prompt: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "You are a careful code repair planner. Output JSON only.\n\n"
                                + prompt
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {"temperature": 0},
        }
        data = await self._post_json(url=url, headers={}, payload=payload)
        return data["candidates"][0]["content"]["parts"][0]["text"]


class OpenAILLMClient(_JSONRestLLMClient):
    """OpenAI chat-completions REST client without requiring the SDK."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def complete(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful code repair planner. Output JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
        }
        data = await self._post_json(
            url=f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            payload=payload,
        )
        return data["choices"][0]["message"]["content"]


def create_llm_client_from_env() -> LLMClient:
    """Create the configured LLM client without requiring external packages."""
    provider = os.environ.get("SCICODEPILOT_LLM_PROVIDER", "").strip().lower()
    mode = os.environ.get("SCICODEPILOT_LLM_MODE", "").strip().lower()

    if not provider and mode == "mock":
        provider = "mock"

    if provider == "mock":
        return MockLLMClient()

    if provider == "deepseek":
        api_key = os.environ.get("SCICODEPILOT_DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            return DisabledLLMClient()
        model = os.environ.get("SCICODEPILOT_DEEPSEEK_MODEL", "deepseek-chat")
        return DeepSeekLLMClient(api_key=api_key, model=model)

    if provider == "gemini":
        api_key = os.environ.get("SCICODEPILOT_GEMINI_API_KEY", "").strip()
        if not api_key:
            return DisabledLLMClient()
        model = os.environ.get("SCICODEPILOT_GEMINI_MODEL", "gemini-1.5-flash")
        return GeminiLLMClient(api_key=api_key, model=model)

    if provider == "openai":
        api_key = os.environ.get("SCICODEPILOT_OPENAI_API_KEY", "").strip()
        if not api_key:
            return DisabledLLMClient()
        model = os.environ.get("SCICODEPILOT_OPENAI_MODEL", "gpt-4o-mini")
        return OpenAILLMClient(api_key=api_key, model=model)

    return DisabledLLMClient()
