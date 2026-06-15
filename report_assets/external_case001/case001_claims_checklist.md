# Case 001 Claims Checklist

## Safe To Say

- We completed one BugsInPy-derived external repair case.
- The system captured an external traceback.
- The system identified `external_assertion_failure` after backend extension.
- The system generated a specialized FailureMemory for this external AssertionError pattern.
- The system generated a conservative source-level PatchPlan.
- The patch was applied in an isolated workspace.
- The original repo was not mutated.
- The rerun command passed with `after_return_code` 0.
- The final status was `patch_success`.

## Do Not Say

- We completed the BugsInPy benchmark.
- We achieved SOTA.
- We can repair arbitrary GitHub repositories.
- External smoke equals real benchmark performance.
- All external failures are supported.
- The original BugsInPy checkout flow succeeded; the source was obtained via GitHub commit ZIP after checkout stalled.

## Suggested Wording

Use: "one BugsInPy-derived external repair success case."

Avoid: "BugsInPy benchmark solved" or "general external repo repair."
