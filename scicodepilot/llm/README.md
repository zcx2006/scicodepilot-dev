# Optional LLM Patch Planner

The LLM patch planner is an optional add-on for SciCodePilot. By default,
SciCodePilot does not use an LLM and still relies on the deterministic
rule-based `PatchPlanner`.

When enabled from CLI, the LLM planner only proposes a `PatchPlan`. It does not
modify files, install dependencies, create missing data, or execute commands.
Any LLM-produced patch still goes through the existing safety flow:

- `PatchProposed`
- `PatchApprovalRequired`
- explicit `confirm_apply`
- isolated workspace patch application
- verification
- hidden evaluator and `score.json`

If a provider is not configured, has no API key, fails, returns invalid JSON, or
returns a low-confidence or empty diff, SciCodePilot falls back to the
rule-based planner.

## Providers

Select a provider with `SCICODEPILOT_LLM_PROVIDER`:

- `mock`
- `deepseek`
- `gemini`
- `openai`
- `disabled`

The old `SCICODEPILOT_LLM_MODE=mock` setting is still supported for M17
compatibility, but `SCICODEPILOT_LLM_PROVIDER=mock` is preferred.

Mock provider for tests and offline demos:

```bash
SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
```

DeepSeek:

```bash
SCICODEPILOT_LLM_PROVIDER=deepseek \
SCICODEPILOT_DEEPSEEK_API_KEY=... \
python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
```

Optional model override:

```bash
SCICODEPILOT_DEEPSEEK_MODEL=deepseek-chat
```

Gemini:

```bash
SCICODEPILOT_LLM_PROVIDER=gemini \
SCICODEPILOT_GEMINI_API_KEY=... \
python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
```

Optional model override:

```bash
SCICODEPILOT_GEMINI_MODEL=gemini-1.5-flash
```

OpenAI:

```bash
SCICODEPILOT_LLM_PROVIDER=openai \
SCICODEPILOT_OPENAI_API_KEY=... \
python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
```

Optional model override:

```bash
SCICODEPILOT_OPENAI_MODEL=gpt-4o-mini
```

Do not write API keys into source code, tests, README examples, shell history
snippets, or logs. ChatGPT Plus/Pro and OpenAI API billing are separate; using
the OpenAI API requires a separate API key and API billing setup.

Future clients can adapt this interface for local models or OpenHands without
replacing the core backend repair workflow.
