# External Case 001: From unsupported failure to verified patch

Subtitle: BugsInPy-derived `youtube-dl Bug 17` external repair workflow

## 3 Key Bullets

- Captured a real external traceback from `youtube-dl`, centered on `assert isinstance(param, bool)`.
- Upgraded the backend path from generic `unsupported_external_failure` to specialized `external_assertion_failure`.
- Applied a conservative source patch only in an isolated workspace and verified the same command passed.

## Before/After Mini Table

| Step | Before backend fix | After backend fix |
|---|---|---|
| Failure type | `unsupported_external_failure` | `external_assertion_failure` |
| FailureMemory | Generic fallback | Specialized |
| Repair plan | `no_op` | Source-level PatchPlan |
| Patch applied | `false` | `true`, isolated workspace only |
| Verification | Not available | `after_return_code = 0` |
| Final status | `unsupported_external_failure` | `patch_success` |

## One-Line Takeaway

SciCodePilot completed one BugsInPy-derived external repair case by turning a captured but unsupported AssertionError into a reviewed workspace patch with successful rerun verification.
