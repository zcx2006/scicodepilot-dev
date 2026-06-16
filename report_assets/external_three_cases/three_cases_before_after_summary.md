# Three External Cases Before/After Summary

## Scope

These are three BugsInPy-derived external cases for `youtube-dl`:

- `case_001`: Bug 17, `cli_bool_option`
- `case_002`: Bug 11, `str_to_int`
- `case_003`: Bug 29, `unified_strdate`

This is not a full BugsInPy benchmark result. The backend extension validates three conservative external repair patterns. In this WSL environment, the original `/mnt/d/.../BugsInPy_Workdir/...` repositories were not present, so Case 002 and Case 003 were verified with minimal local external repos that reproduce the same source patterns.

## Before Backend Extension

| Case | Raw failure | Previous SciCodePilot type | FailureMemory | Repair plan | Patch applied |
|---|---|---|---|---|---|
| case_001 | `AssertionError` | `unsupported_external_failure` | Generic fallback | `no_op` | `false` |
| case_002 | `TypeError` | `unsupported_external_failure` | Generic fallback | `no_op` | `false` |
| case_003 | `AssertionError` | `unsupported_external_failure` | Generic fallback | `no_op` | `false` |

## Backend Extension

- Parser: external source-level AssertionError, external command-level AssertionError, external TypeError, and `pipes` Python-version environment failure.
- FailureMemory: specialized memories for bool assertion, regex TypeError, invalid-date `None` assertion, and environment compatibility.
- PatchPlanner: conservative source-level plans only when narrow patterns match.
- Repair runner: apply only in isolated workspace, rerun the same command, and record before/after status.

## After Backend Extension

| Case | Validation input | Detected type | Patch pattern | Patch applied | After return code | Final status |
|---|---|---|---|---|---|---|
| case_001 | Existing unpatched external workspace copy | `external_assertion_failure` | `params.get(...)` before `assert isinstance(param, bool)` | `true` | `0` | `patch_success` |
| case_002 | Minimal local external repo | `external_type_error` | `str_to_int` None-only guard before `re.sub(..., int_str)` | `true` | `0` | `patch_success` |
| case_003 | Minimal local external repo | `external_assertion_failure` | `unified_strdate(...) is None` command assertion with final `return compat_str(upload_date)` | `true` | `0` | `patch_success` |

## Summary Paths

- Case 001: `external_experiments/scicodepilot_outputs/case_001_repair_after_three_case_fix/summary.json`
- Case 002: `external_experiments/scicodepilot_outputs/case_002_repair_after_three_case_fix/summary.json`
- Case 003: `external_experiments/scicodepilot_outputs/case_003_repair_after_three_case_fix/summary.json`

## Limitations

- Case 001 was rerun against an existing unpatched youtube-dl workspace copy under `external_experiments`.
- Case 002 and Case 003 real repository paths were not available in WSL, so their repair flow was verified on minimal local external repos.
- Python 3.11 was not available in WSL, so the real Bug 29 Python-3.11 path could not be rerun here.
- These results support "three BugsInPy-derived external repair patterns validated", not "BugsInPy benchmark completed".
