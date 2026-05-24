# Report Claims Checklist

This checklist defines claim boundaries for the SciCodePilot final report.

## Allowed Claims

- SciCodePilot evaluates a structured failure-memory pipeline on an internal 10-task controlled benchmark.
- The system diagnoses all controlled tasks under the current benchmark setting.
- The full rule-based repair configuration solves the designed source-code repair tasks under isolated workspace constraints.
- Missing module and missing file cases are routed to `EnvRepairPlan` instead of unsafe automatic modification.
- `PatchSafetyReviewer` blocks predefined unsafe patch patterns in safety stress tests.
- A reproducibility bundle and manifest were generated for the internal controlled experiments.
- A public benchmark adapter skeleton has been prepared for future pilot evaluation.
- The public benchmark adapter is metadata-only at this stage.

## Disallowed Claims

- SciCodePilot achieves SOTA.
- SciCodePilot outperforms SWE-agent / mini-swe-agent / AutoCodeRover.
- SciCodePilot has completed BugsInPy evaluation.
- SciCodePilot has completed SWE-bench evaluation.
- `average_score=1.0` proves real-world generalization.
- Mock LLM repair represents real LLM performance.
- The current internal controlled benchmark is equivalent to a public benchmark.
- The current safety stress tests prove complete sandbox security.

## Preferred Framing

Use "internal controlled benchmark" when discussing current results. Use "future public benchmark pilot" when discussing BugsInPy-style tasks, SWE-bench Lite subsets, or external baseline comparison.
