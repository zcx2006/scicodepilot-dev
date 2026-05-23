# SciCodePilot: A Structured Failure-Memory Agent for Reliable Scientific Code Repair and Reproducibility

## Abstract

- Problem: scientific code repair is brittle when failures are unstructured, patches are unsafe, and environments are hard to reproduce.
- Approach: SciCodePilot turns runtime failures into structured `FailureMemory`, routes environment issues separately, reviews patches before application, and verifies changes in isolated workspaces.
- Evidence: internal 10-task controlled benchmark and ablation study.
- Scope: internal controlled results, not public benchmark or SOTA comparison.

## Introduction

- Motivation: scientific ML code often fails through shape, dtype, device, configuration, dependency, and data-file issues.
- Challenge: repair agents need diagnosis, memory, safety gates, and reproducible execution.
- Contribution summary:
  - Structured failure memory.
  - Explicit diagnosis and repair modes.
  - EnvDoctor routing for environment/data issues.
  - PatchSafetyReviewer and isolated workspace application.
  - Reproducibility bundle and report assets.

## Related Work

- Automated program repair.
- Agentic coding systems.
- Scientific-code benchmarking.
- Reproducibility tooling for Python/conda workflows.
- Safety review and sandboxing for code-generation systems.

## Benchmark and Task Design

- Internal 10-task controlled benchmark.
- Task categories:
  - source-code repair
  - missing module/environment planning
  - missing file/data planning
- Hidden evaluator and `score.json`.
- Isolation rule: original `benchmark/tasks/*/repo` directories are not mutated.

## Method

- BackendController public API.
- Runner and event stream.
- Traceback parser.
- `FailureMemory` schema.
- EnvDoctor routing.
- PatchPlanner and EnvRepairPlan.
- PatchSafetyReviewer.
- Isolated workspace applier.
- Verifier and report-table export.

## Experiments

- Diagnosis suite.
- Repair without apply.
- Repair with confirm apply.
- Mock LLM repair pipeline check.
- Safety stress cases.
- Reproducibility bundle inspection.

## Internal Controlled Ablation

- `diagnosis_only`: diagnosis validation only.
- `repair_without_apply`: planning/review/routing without workspace mutation.
- `full_rule_based_repair`: current main system.
- `mock_llm_repair`: adapter path check, not real LLM performance.
- `safety_stress_cases`: static safety boundary check.

## Safety Analysis

- PatchSafetyReviewer role.
- Approval-required event.
- No automatic dependency installation.
- No automatic missing-data creation.
- No mutation of original benchmark repos.
- Residual risks and future sandbox hardening.

## Limitations

- 10-task benchmark is small.
- `average_score=1.0` only means the controlled tasks were solved.
- No public benchmark yet.
- No external baseline yet.
- Mock LLM is not real LLM evaluation.

## Public Benchmark Extension Plan

- Add public benchmark adapter layer in a future milestone.
- Keep BackendController API stable.
- Preserve safety review and isolated workspace constraints.
- Candidate future work may include BugsInPy, SWE-bench, or mini-swe-agent integration, but this report does not include them.

## Conclusion

- SciCodePilot demonstrates a structured, safety-aware repair pipeline on internal controlled scientific-code failures.
- The current artifact set supports reproducibility and final-report preparation.
