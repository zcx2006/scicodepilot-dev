# External Repo Smoke Summary

- Mode: `diagnosis`
- Repo path: `D:\Git\My_Git_Project\BugsInPy_0616\BugsInPy_Workdir\case_002_bug11\youtube-dl`
- Workspace dir: `D:\Git\My_Git_Project\BugsInPy_0616\external_experiments_0616\branch_results\cases002_003\outputs\bug11_diagnosis\workspace`
- Command: `python -c "from youtube_dl.utils import str_to_int; print(str_to_int(123))"`
- Interpreter: `python`
- Python version: `Python 3.13.5`
- Before return code: `1`
- After return code: `None`
- Patch applied: `False`
- Final status: `patch_failed`
- Scope: External repo smoke interface only; not a public benchmark result and not a SOTA comparison.

## Diagnosis

- Error type: `external_type_error`
- Summary: External TypeError triggered while running the user-provided command.
- Evidence:
  - int_str = re.sub(r'[,\.\+]', '', int_str)
  - TypeError: expected string or bytes-like object, got 'int'

## FailureMemory

- Error type: `external_type_error`
- Root cause hypothesis: External TypeError triggered because a non-string input reached string/regex processing. str_to_int accepts an int input, but the implementation only handles None specially and then passes int_str into re.sub, which expects a string or bytes-like object.
- Repair action: Guard non-string inputs before regex normalization. If the input is not compat_str, return it unchanged.

## Safety Boundary

- The original repo was copied before execution.
- No patch was applied to the original repo.
- This smoke result is not a public benchmark result.
