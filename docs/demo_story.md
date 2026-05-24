# Demo Story

This 5 to 8 minute demo script is designed for a course project presentation. It uses the internal controlled benchmark and does not require API keys, public benchmark downloads, or external baseline execution.

## 1. Problem: Scientific Code Repair Is Brittle

Start with the core problem: scientific Python code often fails for reasons that are small but disruptive. Tensor shapes, dtypes, devices, missing dependencies, missing files, and configuration keys can all break an experiment. A repair agent must know when to patch code, when to route an environment issue, when to stop for safety, and how to preserve reproducibility.

Key line:

> SciCodePilot treats repair as an auditable pipeline rather than a single patch-generation step.

## 2. System Overview

Show the high-level pipeline from `report_assets/figures/system_pipeline.md`.

Narration:

> A benchmark task enters the runner. The traceback parser creates structured `FailureMemory`. `EnvDoctor` routes missing module and missing file cases. Source-code failures go to patch planning, then `PatchSafetyReviewer`, then isolated workspace application and verification.

## 3. Show Event-driven Pipeline

Show `report_assets/figures/event_flow.md`.

Explain that the system emits events such as `TaskStarted`, `CommandStarted`, `CommandOutput`, `ErrorDetected`, `FailureMemoryCreated`, `PatchReviewCreated`, `PatchApprovalRequired`, `PatchApplied`, `VerificationFinished`, and `TaskFinished`.

Demo point:

> The event stream lets us inspect not just whether a task passed, but how the system decided what to do.

## 4. Run Diagnosis

Run the diagnosis suite on the internal controlled benchmark:

```bash
python scripts/run_experiments.py --mode diagnosis
```

Explain that diagnosis validates failure detection and structured memory creation. It does not claim repair success.

## 5. Run Repair Without Apply

Run repair planning without applying patches:

```bash
python scripts/run_experiments.py --mode repair
```

Narration:

> This mode checks routing, patch proposal, and safety review without mutating the isolated workspace. It is useful for showing the system's reasoning before any patch is applied.

## 6. Run Repair With Confirm Apply

Run repair with explicit apply confirmation:

```bash
python scripts/run_experiments.py --mode repair --confirm-apply
```

Explain that approved patches are applied only in isolated workspaces and then verified. Emphasize that original benchmark task repositories are not modified.

## 7. Show Safety Reviewer

Open the safety table:

```bash
cat report_assets/tables/safety_table.md
```

Narration:

> `PatchSafetyReviewer` blocks predefined unsafe patch patterns. This is a static safety boundary for known risky edits, not a proof of complete sandbox security.

## 8. Show Reproducibility Manifest

Open the reproducibility manifest:

```bash
cat report_assets/tables/repro_bundle_manifest.md
```

Explain that the reproducibility manifest records the bundle path, inspected time, git commit, git status, Python version, conda files, pip freeze, GPU info, Docker info, and missing files list.

Key line:

> The reproducibility manifest makes the internal controlled experiment easier to audit and rerun.

## 9. Limitations And Public Benchmark Extension

Close with the boundary:

> The current result is an internal 10-task controlled benchmark. It is not a public benchmark result and not a SOTA comparison.

Then show the public benchmark extension plan:

```bash
cat docs/public_benchmark_plan.md
```

Explain that the next step is a small public benchmark pilot with 3 to 5 lightweight Python tasks, likely starting with a BugsInPy-style pilot before any SWE-bench Lite subset or external baseline comparison.
