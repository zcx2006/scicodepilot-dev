# Three External Cases: Unsupported Failures to Verified Workspace Patches

Subtitle: BugsInPy-derived `youtube-dl` Bugs 17, 11, and 29

## 3 Key Bullets

- Before: all three external cases were captured but ended as `unsupported_external_failure` with generic FailureMemory and `no_op`.
- After: the backend recognizes source-level assertions, command-level assertions, and regex TypeErrors with specialized FailureMemory.
- Verification applies patches only in isolated workspaces and reruns the same command.

## Before/After Mini Table

| Case | Before | After |
|---|---|---|
| Bug 17 | unsupported AssertionError | `external_assertion_failure`, `patch_success` |
| Bug 11 | unsupported TypeError | `external_type_error`, `patch_success` on minimal local repo |
| Bug 29 | unsupported command AssertionError | `external_assertion_failure`, `patch_success` on minimal local repo |

## One-Line Takeaway

SciCodePilot now demonstrates three conservative BugsInPy-derived external repair patterns, while keeping original repos untouched.
