# External Repo Smoke Summary

- Mode: `diagnosis`
- Repo path: `D:\Git\My_Git_Project\LocalSmokeCases\case_assertion_failure`
- Workspace dir: `D:\Git\My_Git_Project\SciCodePilot\scicodepilot-dev-main\outputs\external_smoke\20260609_181112\workspace`
- Command: `python test_case.py`
- Return code: `1`
- Scope: External repo smoke interface only; not a public benchmark result and not a SOTA comparison.

## Diagnosis

- Error type: `unsupported_external_failure`
- Summary: The command failed, but the current external repo smoke interface does not have a specialized parser rule for this failure.
- Evidence:
  - assert len(formats) == 7, f"Expect 7 formats, got {len(formats)}"
  - ^^^^^^^^^^^^^^^^^
  - AssertionError: Expect 7 formats, got 6

## FailureMemory

- Error type: `unsupported_external_failure`
- Root cause hypothesis: The command failed, but the current rule-based memory builder has no specialized hypothesis for this error type.
- Repair action: Inspect the stderr evidence manually and extend the failure-memory rules if this error type should be supported.

## Safety Boundary

- The original repo was copied before execution.
- No patch was applied to the original repo.
- This smoke result is not a public benchmark result.
