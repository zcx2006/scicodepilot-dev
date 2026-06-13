# Demo Transcript

This transcript supports a 5 to 8 minute course-project demo of SciCodePilot. The showcase uses the internal controlled benchmark. It is not a public benchmark and not a SOTA comparison.

## Showcase Goal

Today I will show SciCodePilot as a structured failure-memory agent for scientific code repair and reproducibility. The main idea is that repair should be auditable: we want to see the failure, the structured memory, the routing decision, the patch proposal, the safety review, the verification result, and the reproducibility record.

The demo does not require an API key. It does not download or run public benchmarks. It uses the internal 10-task controlled benchmark.

## Source-code Repair Example

I start with a source-code repair task, `repair_tensor_shape_001`. The task fails because the training code expects a tensor dimension that does not match the model's actual feature size.

I run:

```bash
python scripts/run_showcase_demo.py
```

The first section shows diagnosis for the source-code task. Instead of dumping raw JSON, the script prints a compact human-readable story.

## FailureMemory Summary

The diagnosis creates a `FailureMemory` record. This record captures the error type, evidence from the traceback, a root-cause hypothesis, and the repair action. The important point is that the system does not jump directly from traceback to patch. It first turns the runtime failure into a structured object that downstream components can inspect.

This is one of the core differences between SciCodePilot and a naive patch script: the failure is represented explicitly before repair begins.

## PatchProposal Summary

Next, the demo runs repair without apply. The system emits a `PatchProposal` for the same source-code task. The proposal includes the target file, suspected line, proposed change, confidence, and unified diff.

At this stage the patch is only a proposal. The original benchmark task repository is not modified.

## PatchReview Summary

The proposed patch then passes through `PatchReview`. The demo prints whether the patch is approved, whether it is blocked, and the risk level. This step shows that SciCodePilot does not bypass `PatchSafetyReviewer`.

For the controlled source-code task, the proposed local patch should be reviewable and allowed under the current policy. For unsafe stress cases, the reviewer blocks predefined risky patterns.

## Verification Summary

The demo then runs repair with confirm apply. This applies the approved patch only inside an isolated workspace and runs verification. The output summarizes patch application, verification success, return code, and task completion.

The key point for the presentation is that verification happens after patch application, and the original benchmark task directory remains unchanged.

## EnvRepairPlan Example

The demo also shows an environment-routing task, `repair_missing_module_003`. This task produces an `EnvRepairPlan` instead of a source-code patch.

The `EnvRepairPlan` example demonstrates that missing module and missing file cases are treated as environment or data availability problems. SciCodePilot does not automatically run `pip install`, does not run `conda install`, and does not create fake data.

## SafetyReviewer Example

The safety section summarizes several static safety stress cases:

- A safe local tensor-shape patch.
- A path traversal target.
- An unsafe shell deletion pattern.
- A dependency installation attempt.

The `PatchSafetyReviewer` blocks predefined unsafe patterns before patch application. This supports a narrow safety claim: the reviewer catches the tested risky patch patterns. It is not a proof of complete sandbox security.

## Reproducibility Manifest Mention

The demo closes by pointing to the reproducibility manifest:

```text
report_assets/tables/repro_bundle_manifest.md
```

The reproducibility manifest records the inspected bundle path, git commit, git status, Python version, conda environment files, pip freeze output, GPU information, Docker information, and missing files list.

## Limitations Closing Statement

The current result is based on an internal 10-task controlled benchmark. It is not a public benchmark and not a SOTA comparison. The public benchmark adapter skeleton is available for future pilot work, but no BugsInPy, SWE-bench, or external baseline evaluation is claimed in this report.
