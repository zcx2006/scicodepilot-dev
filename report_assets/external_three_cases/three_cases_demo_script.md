# Three External Cases Demo Script

## 1. Setup

We selected three BugsInPy-derived `youtube-dl` cases: Bug 17, Bug 11, and Bug 29. Before the backend extension, SciCodePilot could copy the external repo and capture stderr, but all three cases ended at `unsupported_external_failure`, generic FailureMemory, and `no_op` repair planning.

## 2. Case 001

Bug 17 fails when `cli_bool_option` reads a missing key with `params.get(...)`, gets `None`, and then reaches `assert isinstance(param, bool)`. The backend now recognizes this as `external_assertion_failure`, generates a None guard PatchPlan, applies it only in the isolated workspace, and reruns successfully.

## 3. Case 002

Bug 11 fails when `str_to_int(123)` sends a non-string value into `re.sub`, causing `TypeError: expected string or bytes-like object`. The backend now recognizes this as `external_type_error` and generates a conservative patch that returns non-`compat_str` values unchanged before regex normalization.

## 4. Case 003

Bug 29 is a command-level assertion: `unified_strdate('not-a-date') is None`. The buggy code converts `upload_date = None` with `compat_str`, producing the string `'None'`. The backend now recognizes the command assertion and patches the final conversion so it only returns when `upload_date is not None`.

## 5. Verification

Each repair is applied only inside a copied workspace, then the same command is rerun. In this environment, Case 001 was rerun on an existing unpatched external workspace copy. Case 002 and Case 003 were verified on minimal local external repos because the original WSL repo paths were missing.

## 6. Limitation

This is not a full BugsInPy benchmark result. It is a conservative validation of three BugsInPy-derived external repair patterns.
