# SciCodePilot: A Structured Failure-Memory Agent for Reliable Scientific Code Repair and Reproducibility

## 1. Abstract

Scientific Python and machine-learning code often fails in ways that are easy for humans to recognize but difficult for automated systems to repair reliably. Shape mismatches, dtype errors, device placement mistakes, missing dependencies, missing data files, and configuration inconsistencies can all stop an experiment before it produces a usable result. SciCodePilot studies a structured approach to this problem: instead of treating repair as a single code-generation step, it represents failures as structured memory, routes environment and data failures separately from source-code patches, reviews proposed patches for safety, applies changes only inside isolated workspaces, and records reproducibility metadata.

This report evaluates SciCodePilot on an internal 10-task controlled benchmark. The current result is an internal controlled benchmark, not a public benchmark and not a SOTA comparison. The system is designed to expose the repair process through events, structured `FailureMemory`, `EnvRepairPlan` records, patch proposals, safety-review events, verification results, and reproducibility manifests. The current evidence supports the claim that this pipeline solves the designed controlled tasks under the project constraints. It does not establish general performance on public bug benchmarks or issue-level repair tasks.

## 2. Introduction

Reliable scientific code repair is difficult because a runtime failure can reflect many different kinds of problems. A tensor shape error may require a local source-code patch. A missing package should usually become an environment plan, not an automatic installation. A missing data file should be surfaced as a data availability issue, not silently fabricated. A generated patch may also be unsafe even when it appears to address the immediate traceback.

SciCodePilot addresses these concerns with a structured failure-memory agent. The system separates diagnosis from repair, converts runtime traces into structured records, routes known environment and data failures through `EnvDoctor`, proposes patches for source-code failures, reviews patches through `PatchSafetyReviewer`, and verifies results in isolated workspaces. The design goal is not only to repair small failures, but also to make the repair process auditable and reproducible.

The project currently uses a 10-task internal controlled benchmark. This benchmark is intentionally small and inspectable. It supports rapid validation of the event stream, failure taxonomy, repair planning, safety review, and reproducibility assets. It should not be presented as evidence of public benchmark performance. A public benchmark pilot is planned as future work through a lightweight adapter skeleton.

## 3. Related Work

SciCodePilot is related to automated program repair, coding agents, scientific workflow reproducibility, and benchmark-driven software engineering evaluation. Automated repair systems often focus on generating candidate patches that satisfy tests. Agentic coding systems broaden that loop by adding planning, tool use, and iterative execution. Scientific-code workflows add additional constraints: dependencies may be fragile, datasets may be external, and errors may reflect experiment configuration rather than ordinary application bugs.

The project also relates to reproducibility tooling for Python and conda environments. A successful repair result is less useful if the source revision, package environment, system metadata, and verification commands cannot be recovered. SciCodePilot therefore treats reproducibility assets as part of the system output rather than an afterthought.

Finally, the project is adjacent to public bug and issue benchmarks such as BugsInPy-style Python benchmarks and SWE-bench Lite. These benchmarks are important future evaluation targets, but they have not been executed in the current report.

## 4. Benchmark and Task Design

The current benchmark contains 10 controlled tasks. The tasks are designed to cover common scientific-code failure modes, including tensor shape mismatches, dtype mismatches, entrypoint errors, label shape errors, device mismatches, loss input errors, collate function errors, configuration key errors, missing modules, and missing files.

The benchmark distinguishes source-code repair tasks from environment and data tasks. Source-code repair tasks are expected to produce patch plans that pass safety review and can be applied in an isolated workspace. Missing module and missing file tasks are expected to produce `EnvRepairPlan` records rather than unsafe automatic modification. This distinction is central to the benchmark: the system is rewarded for recognizing when not to patch source code.

The benchmark is controlled by project-defined tasks and hidden evaluators. It is valuable for internal validation because the expected behavior is clear and repeatable. However, it remains small and curated. It is not a public benchmark and should not be interpreted as a broad measure of real-world generalization.

## 5. Method

SciCodePilot is organized around an event-driven diagnosis and repair pipeline. The public backend interface remains stable through `BackendController.list_tasks()`, `BackendController.get_task(task_id)`, and `BackendController.run_task(task_id, mode, confirm_apply=False)`. The supported modes are diagnosis and repair.

### 5.1 Event-driven Repair Pipeline

Each task run emits structured events that describe the system's progress. A typical flow starts with `TaskStarted`, moves through command execution events such as `CommandStarted` and `CommandOutput`, records detected failures, creates structured failure memory, and then routes toward either environment planning or patch proposal. Repair runs may emit `PatchReviewCreated`, `PatchApprovalRequired`, `PatchApplied`, `VerificationFinished`, and `TaskFinished`.

The event stream makes the system easier to inspect. Rather than reporting only a final score, the pipeline records how the system reached that score and which safety or routing decisions occurred along the way.

### 5.2 Structured FailureMemory

`FailureMemory` is the system's structured representation of a runtime failure. It captures the failure category, traceback-derived information, likely location, and context needed by downstream repair or routing components. This representation helps keep diagnosis separate from patch generation. It also provides a stable unit for analysis in tests, ablations, and report tables.

Structured failure memory is especially useful for scientific code because similar tracebacks can require different actions. A missing module should lead to an environment plan, while a tensor shape error may lead to a source patch. Encoding the distinction explicitly reduces the chance that every failure is treated as a code-editing problem.

### 5.3 Environment and Data Failure Routing

`EnvDoctor` handles missing module and missing file cases. For missing modules, the system creates an `EnvRepairPlan` instead of automatically running package installation commands. For missing files, the system records the data/configuration issue instead of creating fake data. These choices preserve the safety and reproducibility boundary of the experiment.

This routing also clarifies what the current benchmark measures. The system is not claiming that every environment can be fixed automatically. It is demonstrating that environment and data failures can be detected and represented without unsafe side effects.

### 5.4 Patch Planning and Safety Review

For source-code repair tasks, the rule-based patch planner proposes targeted edits. Proposed patches are not applied directly. They pass through `PatchSafetyReviewer`, which checks for predefined unsafe patterns such as path traversal, unsafe shell operations, dependency installation attempts, and other high-risk edits.

The current full repair configuration is the rule-based repair path with safety review and explicit apply confirmation. A mock LLM repair variant exists only to verify that an LLM planner can enter the same safety pipeline. It is not evidence of real LLM repair performance.

### 5.5 Workspace Isolation and Verification

SciCodePilot applies patches in isolated workspaces rather than mutating the original benchmark task directories. After application, a verifier runs the task-specific checks and records results such as `score.json`, event streams, and report tables. This design supports repeatability and protects the original task assets.

Workspace isolation is a practical requirement for repair experiments. It allows the same task to be diagnosed, planned, repaired, and verified repeatedly without corrupting the source benchmark copy.

## 6. Experiments

The experiments are organized around the internal controlled benchmark and ablation suite. The goal is to evaluate whether the system components work together under controlled conditions, not to report public benchmark results.

### 6.1 Internal Controlled Benchmark Setup

The benchmark contains 10 controlled tasks. Each task has a known failure mode and a hidden evaluator. Diagnosis mode validates failure detection and structured memory creation. Repair mode validates routing, patch planning, safety review, patch application when confirmed, and verification.

The current setup uses WSL Ubuntu and the `scicodepilot-dev` conda environment. Reproducibility assets record the source revision, Python version, conda environment exports, package list, system metadata, GPU metadata when present, and Docker metadata when present.

### 6.2 Main Results

Under the current controlled setting, SciCodePilot diagnoses all controlled tasks. The full rule-based repair configuration solves the designed source-code repair tasks under isolated workspace constraints. Missing module and missing file cases are routed to `EnvRepairPlan` rather than unsafe automatic modification.

These results should be read carefully. They show that the designed controlled tasks are handled by the current pipeline. They do not prove broad real-world generalization, public benchmark performance, or superiority over external systems.

### 6.3 Internal Controlled Ablation

The ablation suite includes `diagnosis_only`, `repair_without_apply`, `full_rule_based_repair`, `mock_llm_repair`, and `safety_stress_cases`.

`diagnosis_only` validates failure detection and structured memory creation. It does not represent repair. `repair_without_apply` validates planning, review, and routing without changing the workspace. `full_rule_based_repair` is the current main system configuration. `mock_llm_repair` validates that a planner adapter can enter the same safety pipeline, but it does not represent real LLM performance.

The ablation is therefore best described as an Internal Controlled Ablation Study. It supports component-level interpretation inside the controlled benchmark, not public benchmark ranking.

### 6.4 Safety Stress Cases

Safety stress cases evaluate predefined unsafe patch patterns against `PatchSafetyReviewer`. The goal is to check whether the reviewer blocks known risky edits before application. These tests support the claim that the reviewer enforces static safety boundaries for the predefined cases.

The safety tests do not prove complete sandbox security. They are a focused validation of known unsafe patch patterns and should be reported with that scope.

### 6.5 Reproducibility Bundle

The reproducibility bundle captures the source revision, git status, Python version, conda environment files, pip freeze output, system metadata, GPU information, Docker version information, and Docker image metadata. The exported manifest records whether expected files are present and lists missing files if any are absent.

For the current M23A bundle inspection, the manifest was generated successfully and reported no missing files. The bundle supports reproducibility for internal controlled experiments. It does not convert the internal benchmark into a public benchmark evaluation.

### 6.6 External Repo Smoke Interface

M26 adds a lightweight external repo smoke interface for local Python repositories. The interface copies a user-provided repo into an isolated workspace, runs a user-provided command, captures stdout, stderr, and return code, and then produces a diagnosis summary. In repair-plan mode, it can produce an `EnvRepairPlan` for missing module or missing file failures, or a non-applying `PatchPlan` plus `PatchSafetyReviewer` summary for supported source-code failures.

This interface is a smoke tool, not a public benchmark result. It does not download BugsInPy or SWE-bench, does not run external baselines, and does not apply patches to the original repo. Unsupported external failures are reported as `unsupported_external_failure` with a no-op plan.

### 6.7 Memory Retrieval Evaluation

M28 evaluates whether deterministic `FailureMemory` retrieval can recover relevant internal controlled benchmark memory records. The evaluation reads local JSONL memory records, uses each record as a controlled query, retrieves top-k similar records with embedding-free token matching, and reports self-match, same-error-type, and same-category retrieval metrics.

This is a component-level retrieval sanity check scoped to internal controlled benchmark records. It does not evaluate real LLM repair performance, does not report public benchmark performance, and does not compare against external systems. The current memory data has one record per controlled error type, so exact self retrieval is useful as a reproducibility check while same-error retrieval beyond the identical record remains limited by data size.

## 7. Public Benchmark Extension Plan

The next evaluation step is a small public benchmark pilot. The recommended priority is a BugsInPy-style pilot first, followed by a small SWE-bench Lite subset, and only later an external baseline comparison. The initial pilot should use 3 to 5 Python tasks with pytest-based validation, short runtimes, and light dependencies.

M23B prepared a metadata-only public benchmark adapter skeleton. The skeleton defines `PublicBenchmarkTask` records and placeholder registry entries. It does not download repositories, install benchmark environments, run public tests, or produce public benchmark results.

This future work has several risks. Environment installation may be expensive, Docker and conda versions may conflict, task runtime may be too long, issue-level repair may exceed the current rule-based planner's capabilities, and `PatchSafetyReviewer` may be conservative for some public benchmark patches. These risks should be addressed before any public benchmark numbers are reported.

## 8. Limitations

The current benchmark has only 10 controlled tasks. The tasks are useful for system validation, but they are not representative of the full diversity of scientific Python failures.

An `average_score` of 1.0 on controlled tasks means that the designed tasks were solved under the benchmark's constraints. It does not prove real-world generalization. The project also lacks completed public benchmark evaluation and external baseline execution in the current report.

The mock LLM repair path is not a real LLM evaluation. It only checks that a planner adapter can enter the same safety pipeline. Similarly, safety stress cases validate predefined unsafe patterns, not every possible unsafe edit.

## 9. Conclusion

SciCodePilot demonstrates a structured failure-memory approach to reliable scientific code repair and reproducibility. On the internal 10-task controlled benchmark, the system diagnoses all controlled tasks, routes environment and data failures without unsafe automatic modification, repairs designed source-code failures through the full rule-based configuration, applies patches in isolated workspaces, and records reproducibility assets.

The current contribution is a controlled, auditable repair pipeline and a report-ready evaluation pack. The next step is a carefully scoped public benchmark pilot, reported separately and without overstating the current internal controlled results.
