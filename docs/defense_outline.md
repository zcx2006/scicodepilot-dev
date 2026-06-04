# Defense Outline

## 1. Project One-sentence Positioning

SciCodePilot is a structured failure-memory agent for reliable scientific Python/ML code repair and reproducibility, evaluated on an internal controlled benchmark and component-level assets.

## 2. Problem Motivation

Scientific code often fails for practical reasons: tensor shapes, dtypes, device placement, missing dependencies, missing files, config keys, and data-loader contracts. A useful repair system should diagnose the failure, decide whether it is source-code or environment/data related, review safety risks, verify changes, and preserve reproducibility.

## 3. Why Direct LLM Patching Is Not Enough

Direct patching can blur diagnosis, repair, safety, and verification into one opaque step. SciCodePilot separates those responsibilities so a reviewer can inspect what failed, why a plan was produced, whether it passed safety review, and what verification proved.

## 4. System Pipeline

The pipeline starts from a benchmark task or local command, runs it in a controlled workspace, parses the traceback, creates `FailureMemory`, routes to `EnvDoctor` or `PatchPlanner`, reviews patches through `PatchSafetyReviewer`, applies approved internal benchmark patches only in isolated workspaces, and writes report/reproducibility assets.

## 5. Key Design Choices

- Structured events make the run auditable.
- `FailureMemory` keeps diagnosis separate from repair.
- `EnvDoctor` routes dependency and data issues without automatic installation or fake data creation.
- `PatchSafetyReviewer` blocks known unsafe patch patterns before application.
- Isolated workspaces protect original benchmark tasks.
- Reproducibility manifests make the environment inspectable.
- Deterministic memory retrieval supports component-level analysis without embeddings or network calls.

## 6. Internal Controlled Benchmark

The current benchmark has 10 controlled tasks: 8 source-code repair tasks and 2 environment/data routing tasks. It is intentionally small and inspectable, so it is useful for validating the system pipeline. It is not public benchmark evaluation.

## 7. Main Results

The internal controlled run reports diagnosis pass count `10/10`, patch plan count `8`, env repair plan count `2`, patch review count `8`, patch applied count `8`, verification success count `8`, scored task count `8`, average score `1.0`, and safety stress case pass count `10`.

These results are scoped to internal controlled tasks and component-level evaluation.

## 8. FailureMemory Retrieval Contribution

M27 and M28 turn `FailureMemory` into a local JSONL memory store with deterministic token-based retrieval. The retrieval evaluation checks whether controlled queries recover relevant memory records. It does not call a real LLM and does not measure real LLM repair performance.

## 9. Safety And Reproducibility

SciCodePilot keeps safety and reproducibility visible: unsafe patch patterns are reviewed before application, missing dependencies and files become plans rather than automatic changes, patches are applied only in isolated internal benchmark workspaces, and the reproducibility bundle records source/environment/system metadata.

## 10. External Repo Smoke Interface

The external repo smoke interface copies a local Python repo into an isolated workspace, runs a user-provided command, and produces diagnosis or non-applying repair-plan summaries. It proves there is a local smoke entry point beyond built-in benchmark tasks. It does not prove public benchmark performance and does not mutate the original repo.

## 11. Limitations

The benchmark has only 10 controlled tasks. The rule-based planner is limited. Memory retrieval is deterministic string matching. Mock LLM behavior is not real LLM evaluation. Public benchmark adapters are metadata skeletons only.

## 12. Future Work

Future work should run a small public benchmark pilot, expand failure types, evaluate a real structured planner under the same safety pipeline, add more memory records, and compare against external systems only after a fair public benchmark protocol exists.

## 13. Likely Q&A

**How is SciCodePilot different from asking ChatGPT to fix code?**

It separates diagnosis, memory, routing, safety review, isolated application, verification, and reproducibility instead of treating repair as a single free-form response.

**What exactly is `FailureMemory`?**

It is a structured record of a failure: error type, evidence, root-cause hypothesis, and recommended repair action. M27 extends it into JSONL memory records for retrieval.

**Why are there only 10 benchmark tasks?**

The current benchmark is controlled and project-defined so each pipeline component can be validated clearly. Larger public benchmark evaluation is future work.

**Did you run BugsInPy or SWE-bench?**

No. The project includes a public benchmark adapter skeleton and plan, but no public benchmark execution is claimed.

**Is the memory retrieval just string matching?**

Yes. It is deterministic token matching with bonuses for matching error type, exception type, and path-like terms. That is deliberate for offline reproducibility.

**Does the system use a real LLM?**

No real LLM is required for the current evaluation. Mock LLM paths and prompt builders are for pipeline compatibility and future planning.

**Why not automatically install missing packages?**

Automatic installation can change the environment unpredictably. SciCodePilot creates an `EnvRepairPlan` so a human can decide how to modify the environment.

**Why not create missing data files?**

Creating fake data can hide the real reproducibility problem. Missing files are surfaced as data/config availability issues.

**What does `PatchSafetyReviewer` protect against?**

It checks predefined unsafe patterns such as path traversal, unsafe shell commands, dependency installation attempts, blocked target areas, and multi-file changes.

**What does external repo smoke test prove and not prove?**

It proves the system can run a local command in a copied workspace and produce diagnosis or non-applying repair-plan artifacts. It does not prove public benchmark performance.

**What is the biggest limitation?**

The evaluation is small and controlled, so it does not establish broad real-world behavior.

**What would you do next with more time?**

Run a 3 to 5 task public benchmark pilot, expand memory records, evaluate a real structured planner under the same safety pipeline, and then consider external baseline comparison.
