# Case 001 Demo Script

## 1. What failed before?

This external case comes from BugsInPy-derived `youtube-dl Bug 17`. The minimal command called `cli_bool_option` with a missing option key. In the buggy version, `params.get(param)` returned `None`, then the code reached `assert isinstance(param, bool)` and raised `AssertionError`.

Before the backend fix, SciCodePilot captured the external traceback, but classified it as `unsupported_external_failure`.

## 2. What SciCodePilot diagnosed?

The original diagnosis showed the right evidence: `assert isinstance(param, bool)` and `AssertionError`. However, because the external AssertionError pattern was unsupported, FailureMemory fell back to a generic explanation and the repair plan was `no_op`.

## 3. What changed in backend?

We added a conservative external AssertionError path: parse the last application traceback frame, extract the assertion expression, build specialized FailureMemory, and generate a PatchPlan only when the code matches a narrow pattern: `dict.get(...)` followed by `assert isinstance(<var>, bool)`.

## 4. What patch was generated?

SciCodePilot generated this source-level patch for `youtube_dl/utils.py`:

```python
param = params.get(param)
if param is None:
    return []
assert isinstance(param, bool)
```

The patch was safety-reviewed and applied only inside the isolated workspace.

## 5. How did verification prove success?

The same command was rerun after patching. Before patching, the return code was `1`. After patching, the return code was `0`, stdout was `[]`, and the final status became `patch_success`. The summary records `original_repo_mutated: false`.

## 6. What is the limitation?

This is not a full BugsInPy benchmark result. This is one external repair success case used to validate the workflow. The backend rule is intentionally narrow and should not be presented as support for arbitrary GitHub repositories or all external failures.
