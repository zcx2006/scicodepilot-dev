# Final Claims Checklist

## Safe Claims

- SciCodePilot evaluates an internal controlled benchmark.
- SciCodePilot reports component-level evaluation assets.
- SciCodePilot uses structured `FailureMemory`.
- SciCodePilot separates diagnosis from repair.
- SciCodePilot routes source-code failures separately from env/data failures.
- SciCodePilot uses safety-constrained patch planning.
- SciCodePilot verifies approved internal benchmark repairs in isolated workspaces.
- SciCodePilot exports a reproducibility manifest.
- SciCodePilot includes an external repo smoke interface.
- SciCodePilot includes deterministic memory retrieval evaluation.

## Claims That Need Qualification

- "The system solves the benchmark" must specify the internal 10-task controlled benchmark.
- "The memory retrieval works" must specify deterministic token matching over internal controlled records.
- "The LLM planner path exists" must specify mock/prompt-building behavior unless real LLM evaluation is added later.
- "The external repo interface works" must specify smoke diagnosis/planning only, with copied workspaces.
- "Safety reviewer blocks unsafe patches" must specify predefined unsafe patterns, not complete sandbox security.

## Prohibited Claims

- SOTA.
- Outperforms SWE-agent / AutoCodeRover / OpenHands / other agents.
- Completed SWE-bench.
- Completed BugsInPy.
- Public benchmark performance.
- Real-world generalization.
- Real LLM repair performance.
- Fully secure sandbox.
- Automatic environment repair.
- Automatic dataset repair.

## Recommended One-Sentence Project Claim

SciCodePilot is a structured failure-memory agent that demonstrates a safety- and reproducibility-aware repair pipeline on an internal controlled scientific Python benchmark.

## Recommended Result Claim

On the internal 10-task controlled benchmark, SciCodePilot diagnoses all controlled tasks, plans eight source-code repairs, routes two env/data failures, applies eight approved patches in isolated workspaces, and exports component-level report assets.

## Recommended Limitation Statement

The current evaluation is small and controlled; it does not establish public benchmark performance, external baseline comparison, real LLM repair performance, or broad real-world behavior.
