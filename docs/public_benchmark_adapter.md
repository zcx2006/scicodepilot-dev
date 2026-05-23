# Public Benchmark Adapter Skeleton

The public benchmark adapter is a metadata skeleton for future public benchmark pilots. It does not download repositories, install dependencies, run benchmark tests, or report completed public benchmark results.

## PublicBenchmarkTask Schema

`PublicBenchmarkTask` records the minimal metadata needed to plan a future benchmark adapter:

- `task_id`: local identifier for the pilot task.
- `source`: benchmark family or placeholder source.
- `repo`: repository name or URL metadata.
- `commit`: target commit metadata for checkout.
- `issue_or_bug_id`: upstream issue, bug, or instance identifier.
- `setup_command`: future setup command metadata.
- `test_command`: future failing or verification test command metadata.
- `expected_failure_type`: expected broad failure category.
- `notes`: scope and execution notes.

Current placeholder tasks use notes stating: `metadata placeholder only; not executed in current report`.

## Future Workflow

```text
metadata
-> checkout repo
-> setup env
-> run failing test
-> SciCodePilot diagnosis/repair
-> isolated patch
-> run verification
```

The future adapter should preserve the existing SciCodePilot safety rules:

- Do not bypass `PatchSafetyReviewer`.
- Do not mutate original benchmark repositories.
- Do not auto-install dependencies without explicit setup policy.
- Do not change the stable `BackendController` public API.

## Reporting Boundary

This adapter is only a skeleton. It should not be described in reports as a completed public benchmark evaluation, a SWE-bench result, a BugsInPy result, or an external baseline comparison.
