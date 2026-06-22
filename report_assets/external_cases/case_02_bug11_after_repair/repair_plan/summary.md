# External Repo Smoke Summary

- Mode: `repair-plan`
- Repo path: `D:\Git\My_Git_Project\BugsInPy_0616\BugsInPy_Workdir\case_002_bug11\youtube-dl`
- Workspace dir: `D:\Git\My_Git_Project\BugsInPy_0616\external_experiments_0616\branch_results\cases002_003\outputs\bug11_repair_plan\workspace`
- Command: `python -c "from youtube_dl.utils import str_to_int; print(str_to_int(123))"`
- Interpreter: `python`
- Python version: `Python 3.13.5`
- Before return code: `1`
- After return code: `None`
- Patch applied: `False`
- Final status: `repair_plan_only`
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

## Repair Planning

- Plan type: `PatchPlan`
- Note: Patch was reviewed only; no patch was applied.
- PatchPlan target: `youtube_dl/utils.py`
- PatchPlan change: Replace the None-only guard with a compat_str type guard so non-string inputs are returned unchanged before regex normalization.
- PatchPlan diff:

```diff
--- youtube_dl/utils.py
+++ youtube_dl/utils.py
@@ -3519,8 +3519,8 @@
 
 def str_to_int(int_str):
     """ A more relaxed version of int_or_none """
-    if int_str is None:
-        return None
+    if not isinstance(int_str, compat_str):
+        return int_str
     int_str = re.sub(r'[,\.\+]', '', int_str)
     return int(int_str)
 
```
- Safety notes:
  - Pattern matched only str_to_int with an exact None-only guard.
  - Patch requires a later re.sub(..., int_str) call in the same function.
  - Patch is limited to the isolated workspace target file.
- PatchSafetyReviewer: approved=True blocked=False risk=low

## Safety Boundary

- The original repo was copied before execution.
- No patch was applied to the original repo.
- This smoke result is not a public benchmark result.
