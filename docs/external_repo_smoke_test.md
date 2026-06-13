# External Repo Smoke Test

The external repo smoke interface provides a lightweight way to run SciCodePilot-style diagnosis and repair planning against an arbitrary local Python repository. Its purpose is to show that the system entry point is not limited to the internal `benchmark/tasks` runner.

This feature is a smoke interface only. It is not a public benchmark, not a SOTA comparison, and not a replacement for BugsInPy or SWE-bench evaluation.

## Usage

Run diagnosis on a local repo:

```bash
python scripts/run_external_repo_smoke.py --repo-path /path/to/repo --command "pytest -q"
```

Run non-applying repair planning:

```bash
python scripts/run_external_repo_smoke.py --repo-path /path/to/repo --command "pytest -q" --mode repair-plan
```

By default, the script copies the repo into an isolated workspace:

```text
outputs/external_smoke/<timestamp>/workspace
```

The command runs inside that copied workspace. The original repo is not mutated.

## Outputs

The script writes:

```text
outputs/external_smoke/<timestamp>/summary.md
outputs/external_smoke/<timestamp>/summary.json
```

`summary.md` is a human-readable report with the command result, parsed error type, evidence, `FailureMemory` summary, and optional non-applying repair plan.

`summary.json` records the same information in structured form, including stdout, stderr, return code, copied workspace path, parsed error, failure memory, and repair-plan metadata when requested.

## Repair Planning Boundary

In `repair-plan` mode:

- Missing module failures produce an `EnvRepairPlan`.
- Missing file failures produce an `EnvRepairPlan`.
- Supported source-code failures may produce a `PatchPlan` and `PatchSafetyReviewer` result.
- Unsupported external failures produce `unsupported_external_failure` and a no-op plan.
- No patch is applied by default.
- No patch is applied to the original repo.

The script does not bypass `PatchSafetyReviewer`.

## Current Limitations

The external smoke interface is intentionally small. It reuses the current rule-based traceback parsing and planning components, which were designed for the internal controlled benchmark. Many real external repo failures will therefore be reported as `unsupported_external_failure`.

This is expected. The purpose is to provide a safe local entry point for smoke diagnosis and planning, not to claim public benchmark performance.

## Future Pilot Use

A future pilot can use this interface on one real local Python bug by:

1. Cloning or preparing a small repo manually.
2. Confirming the failing command is short-running and dependency-light.
3. Running diagnosis with `--mode diagnosis`.
4. Running non-applying repair planning with `--mode repair-plan`.
5. Inspecting `summary.md`, `summary.json`, and the copied workspace.
6. Deciding whether the failure type should become a supported adapter case.

That future pilot should still be reported separately from the internal controlled benchmark.
