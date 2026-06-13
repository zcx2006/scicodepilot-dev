# m30_external_pilot_results

# M30 External Pilot Results

## Objective

Evaluate the feasibility of applying SciCodePilot to external Python repositories and public benchmark-style bugs.

------

## Experiment 1: BugsInPy Feasibility

### Target Project

```text
youtube-dl
```

### Attempted Bugs

| Bug ID | Result  | Notes                                          |
| ------ | ------- | ---------------------------------------------- |
| bug 1  | Failed  | GitHub clone / network failure                 |
| bug 2  | Success | Checkout completed and failing test reproduced |
| bug 3  | Failed  | Repository setup failure                       |
| bug 4  | Failed  | Repository setup failure                       |

------

## Experiment 2: External Smoke Interface

### Case A: BugsInPy youtube-dl bug 2

Observed:

```text
Failing unittest successfully reproduced
```

External Smoke Output:

```text
summary.md
summary.json
```

Result:

```text
Failure evidence captured successfully
```

------

### Case B: Local Assertion Failure Fallback

Repository:

```text
LocalSmokeCases/case_assertion_failure
```

Command:

```bash
python test_case.py
```

Observed Failure:

```text
AssertionError: Expect 7 formats, got 6
```

External Smoke Output:

```text
summary.md
summary.json
```

Result:

```text
Failure captured successfully
```

------

## External Pilot Summary

| Experiment                   | Status    |
| ---------------------------- | --------- |
| BugsInPy feasibility         | Completed |
| BugsInPy successful bug run  | 1         |
| Additional BugsInPy attempts | 3         |
| Local fallback smoke         | Completed |
| External smoke interface     | Verified  |

------

## Key Findings

1. SciCodePilot can process failures from external Python repositories.
2. External Smoke successfully captures failure evidence and generates structured summaries.
3. Real-world benchmark execution is often affected by environment and network issues.
4. Local fallback smoke provides a reproducible backup evaluation path.