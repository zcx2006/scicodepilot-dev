"""Optional LLM-assisted patch planning components."""

from scicodepilot.llm.llm_client import (
    DeepSeekLLMClient,
    DisabledLLMClient,
    GeminiLLMClient,
    LLMClient,
    MockLLMClient,
    OpenAILLMClient,
)

__all__ = [
    "DeepSeekLLMClient",
    "DisabledLLMClient",
    "GeminiLLMClient",
    "LLMClient",
    "MockLLMClient",
    "OpenAILLMClient",
    "LLMPatchPlanner",
]


def __getattr__(name: str):
    if name == "LLMPatchPlanner":
        from scicodepilot.llm.llm_patch_planner import LLMPatchPlanner

        return LLMPatchPlanner
    raise AttributeError(name)
