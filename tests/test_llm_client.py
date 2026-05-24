import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.llm.llm_client import (
    DisabledLLMClient,
    MockLLMClient,
    create_llm_client_from_env,
)


@pytest.mark.asyncio
async def test_mock_llm_client_is_deterministic() -> None:
    prompt = (
        "task_id: repair_tensor_shape_001\n"
        "error_type: tensor_shape\n"
        "source_code:\n"
        "    classifier_expected_dim = 128\n"
    )
    client = MockLLMClient()

    first = await client.complete(prompt)
    second = await client.complete(prompt)

    assert first == second
    data = json.loads(first)
    assert data["target_file"] == "train.py"
    assert data["unified_diff"]


@pytest.mark.asyncio
async def test_disabled_llm_client_returns_empty_completion() -> None:
    assert await DisabledLLMClient().complete("prompt") == ""


def clear_llm_env(monkeypatch) -> None:
    for name in [
        "SCICODEPILOT_LLM_PROVIDER",
        "SCICODEPILOT_LLM_MODE",
        "SCICODEPILOT_DEEPSEEK_API_KEY",
        "SCICODEPILOT_GEMINI_API_KEY",
        "SCICODEPILOT_OPENAI_API_KEY",
    ]:
        monkeypatch.delenv(name, raising=False)


def test_create_llm_client_from_env_provider_mock(monkeypatch) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("SCICODEPILOT_LLM_PROVIDER", "mock")

    assert isinstance(create_llm_client_from_env(), MockLLMClient)


def test_create_llm_client_from_env_legacy_mode_mock(monkeypatch) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("SCICODEPILOT_LLM_MODE", "mock")

    assert isinstance(create_llm_client_from_env(), MockLLMClient)


def test_create_llm_client_from_env_provider_disabled(monkeypatch) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("SCICODEPILOT_LLM_PROVIDER", "disabled")

    assert isinstance(create_llm_client_from_env(), DisabledLLMClient)


def test_create_llm_client_from_env_defaults_to_disabled(monkeypatch) -> None:
    clear_llm_env(monkeypatch)

    assert isinstance(create_llm_client_from_env(), DisabledLLMClient)


@pytest.mark.parametrize("provider", ["deepseek", "gemini", "openai"])
def test_create_llm_client_from_env_provider_without_api_key_is_disabled(
    monkeypatch,
    provider: str,
) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("SCICODEPILOT_LLM_PROVIDER", provider)

    assert isinstance(create_llm_client_from_env(), DisabledLLMClient)
