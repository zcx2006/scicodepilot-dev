# Internal Controlled Ablation Study

This document reframes the current SciCodePilot ablation results for final-report use. The study is an internal controlled ablation, not a public benchmark and not a SOTA comparison.

## Study Scope

The benchmark currently contains 10 controlled tasks designed to exercise failure diagnosis, structured failure memory, patch planning, environment repair routing, static safety review, isolated application, and verification.

The goal is to validate whether the current system components work together on known controlled cases. The goal is not to claim broad generalization across public scientific-code repair benchmarks.

## Scenarios

| Scenario | Purpose | Interpretation |
| --- | --- | --- |
| `diagnosis_only` | Runs tasks in diagnosis mode. | Validates diagnosis events, traceback parsing, and `FailureMemory`; it does not represent repair. |
| `repair_without_apply` | Runs repair mode without apply confirmation. | Validates planning, review, and routing while leaving the workspace unchanged. |
| `full_rule_based_repair` | Runs the current main system with rule-based repair. | Measures the current controlled repair path with safety review and isolated application. |
| `mock_llm_repair` | Sends a mock LLM planner through the repair flow. | Verifies that an LLM planner can enter the same safety pipeline; it does not represent real LLM performance. |
| `safety_stress_cases` | Exercises unsafe patch examples. | Validates static safety boundaries enforced by `PatchSafetyReviewer`. |

## Interpretation

The `full_rule_based_repair` scenario is the current main system configuration for controlled repair tasks. It should be reported as the internal controlled result, not as a public benchmark score.

The `diagnosis_only` scenario only verifies the diagnostic half of the pipeline. A successful diagnosis result means the system can identify and structure failures, not that it can repair them.

The `repair_without_apply` scenario is useful for checking planning, review, and routing behavior without mutating an isolated workspace. It is intentionally conservative and should not be interpreted as final repair success.

The `mock_llm_repair` scenario only checks adapter and pipeline compatibility. Because the planner is mocked, it is not a substitute for real LLM evaluation.

The `safety_stress_cases` scenario probes static safety checks. It does not prove complete sandbox security; it confirms that known unsafe patch patterns are blocked by `PatchSafetyReviewer`.

## Limitations

- The benchmark has only 10 controlled tasks, so it is small.
- `average_score=1.0` means the controlled tasks were successfully solved; it does not imply broad real-world repair performance.
- The current study does not include a public benchmark.
- The current study does not include an external baseline.
- Mock LLM repair is not equivalent to real LLM evaluation.
- The current results should be described as an internal controlled benchmark, not a public benchmark or SOTA comparison.

## Report Language

Recommended wording:

> On the internal 10-task controlled benchmark, SciCodePilot solves the designed repair tasks under the full rule-based repair configuration while preserving the safety-review and isolated-workspace constraints.

Avoid wording that implies public benchmark leadership, SOTA performance, or strong external baseline comparison.
