# External Repo Smoke Summary

- Mode: `repair-plan`
- Repo path: `D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_002_bug11\youtube-dl`
- Workspace dir: `D:\Git\My_Git_Project\Bugs_2nd_try\external_experiments\scicodepilot_outputs\case_002_repair_plan\workspace`
- Command: `python -c "from youtube_dl.utils import str_to_int; print(str_to_int(123))"`
- Return code: `1`
- Scope: External repo smoke interface only; not a public benchmark result and not a SOTA comparison.

## Diagnosis

- Error type: `unsupported_external_failure`
- Summary: The command failed, but the current external repo smoke interface does not have a specialized parser rule for this failure.
- Evidence:
  - return _compile(pattern, flags).sub(repl, string, count)
  - ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  - TypeError: expected string or bytes-like object, got 'int'

## FailureMemory

- Error type: `unsupported_external_failure`
- Root cause hypothesis: The command failed, but the current rule-based memory builder has no specialized hypothesis for this error type.
- Repair action: Inspect the stderr evidence manually and extend the failure-memory rules if this error type should be supported.

## Repair Planning

- Plan type: `no_op`
- Note: unsupported_external_failure: current system can only generate a diagnosis summary or no-op plan for this external failure.

## Safety Boundary

- The original repo was copied before execution.
- No patch was applied to the original repo.
- This smoke result is not a public benchmark result.
