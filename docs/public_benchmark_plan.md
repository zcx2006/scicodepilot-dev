# Public Benchmark Pilot Plan

SciCodePilot currently reports results on a 10-task internal controlled benchmark. This benchmark is useful for validating the system pipeline because each task is small, inspectable, and designed to exercise a known failure mode. It should only be described as an internal controlled benchmark because it is project-defined, limited in scale, and does not measure performance against an external public task distribution.

The current result is not a public benchmark result and not a SOTA comparison. It demonstrates that the structured failure-memory pipeline can solve the controlled tasks under the current evaluation constraints.

## Why Add A Public Benchmark Pilot

A public benchmark pilot would test whether SciCodePilot's diagnosis, repair planning, patch review, isolated application, and verification workflow can transfer beyond hand-designed controlled tasks. The pilot should be small at first so that environment setup, runtime, task selection, and safety-review behavior can be understood before committing to larger benchmark execution.

## Candidate Benchmarks

- BugsInPy / Tests4Py-style Python bug benchmark: Python-focused bug tasks with pytest-style validation are the best fit for a first pilot.
- SWE-bench Lite subset: useful for issue-level repository repair, but likely harder because tasks may require broader code understanding and heavier setup.
- mini-swe-agent as possible external baseline: useful later as a comparison point, not part of the current skeleton.

## Recommended Priority

1. BugsInPy-style pilot.
2. SWE-bench Lite small subset.
3. External baseline comparison.

## Current Reporting Boundary

At the current stage, the project should not claim public benchmark results, external baseline wins, or SOTA performance. Any report language should clearly separate the completed internal controlled benchmark from the planned public benchmark pilot.

## Risks

- Environment installation costs may dominate small task runs.
- Docker and conda versions may conflict with benchmark-specific setup scripts.
- Individual task runtime may be too long for rapid iteration.
- Issue-level repair can exceed the current rule-based planner's capabilities.
- `PatchSafetyReviewer` may be too conservative for some public benchmark patches.

## Pilot Scope

The recommended first pilot is 3 to 5 public tasks. Select only tasks that are:

- Python-based.
- Validated by pytest or a similarly lightweight command.
- Short-running.
- Light on dependencies.
- Clear about the failing test and expected repair surface.

The pilot should be implemented as metadata-driven adapters first, followed by controlled checkout/setup/execution only after the skeleton is reviewed.
