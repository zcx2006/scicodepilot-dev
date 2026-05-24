# Ablation Study

## Purpose

The ablation study separates diagnosis, planning, confirmation, repair, mock LLM
planning, and safety stress cases so the final report can explain which part of
SciCodePilot contributes to reliability and safety.

This project is not a train/validation/test machine-learning setup. It is a
controlled benchmark task evaluation: each task is a reproducible scientific
code failure with an expected diagnosis and, where appropriate, a deterministic
repair target.

## Variants

### diagnosis_only

Runs `python scripts/run_benchmark_suite.py --mode diagnosis`.

This variant validates error detection, TracebackParser, FailureMemoryBuilder,
and diagnosis evaluation. It proves recognition and explanation, not repair.

### repair_without_apply

Runs `python scripts/run_benchmark_suite.py --mode repair`.

This variant validates PatchPlan generation, EnvDoctor routing, and
PatchReviewCreated without modifying code. It should produce patch plans and
safety reviews, but `patch_applied_count` remains zero.

### full_rule_based_repair

Runs `python scripts/run_benchmark_suite.py --mode repair --confirm-apply`.

This is the main system result. It validates deterministic patch planning,
PatchSafetyReviewer, isolated workspace application, verification, score.json,
and env/data routing.

### mock_llm_repair

Runs `SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner`.

This variant validates that an LLM PatchPlanner can enter the same safety
pipeline. It also shows that mock LLM patches are constrained by
PatchReviewCreated and workspace isolation.

### safety_stress_cases

Runs `python -m pytest tests/test_patch_safety_reviewer.py -q`.

This variant validates that PatchSafetyReviewer blocks dangerous or
out-of-bound patches such as path traversal, `pip install`, `rm -rf`, and
multi-file diffs.
