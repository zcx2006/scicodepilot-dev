# m30_failure_analysis

## Background

M30 introduced external pilot experiments to evaluate SciCodePilot beyond the internal benchmark.

These experiments revealed several practical failure modes.

------

# Case 1: BugsInPy youtube-dl bug 2

Observed Failure:

```text
AssertionError / failing unittest
```

External Smoke Classification:

```text
unsupported_external_failure
```

Issue:

Although the failure was captured successfully, it was not classified into a dedicated assertion-related category.

------

# Case 2: BugsInPy bug 1

Observed Failure:

```text
Git clone failure
RPC failed
Connection reset
```

Classification:

```text
setup_failure
```

Root Cause:

Network instability during repository checkout.

------

# Case 3: BugsInPy bug 3

Observed Failure:

```text
Repository setup failure
```

Classification:

```text
setup_failure
```

------

# Case 4: BugsInPy bug 4

Observed Failure:

```text
Repository setup failure
```

Classification:

```text
setup_failure
```

------

# Case 5: Local Assertion Failure Smoke

Repository:

```text
LocalSmokeCases/case_assertion_failure
```

Observed Failure:

```text
AssertionError: Expect 7 formats, got 6
```

Result:

External Smoke successfully captured the failure and generated summary artifacts.

This confirms that the external smoke interface functions correctly even when public benchmark setup fails.

------

# Failure Taxonomy

| Case             | Failure Type    | Classification               |
| ---------------- | --------------- | ---------------------------- |
| youtube-dl bug 2 | AssertionError  | unsupported_external_failure |
| bug 1            | Network failure | setup_failure                |
| bug 3            | Setup failure   | setup_failure                |
| bug 4            | Setup failure   | setup_failure                |
| local smoke      | AssertionError  | captured successfully        |

------

# Key Findings

## Finding 1

Assertion-based failures can be captured successfully.

------

## Finding 2

Current taxonomy does not contain:

```text
assertion_failure
unittest_failure
pytest_failure
```

As a result:

```text
AssertionError
```

is currently mapped to:

```text
unsupported_external_failure
```

------

## Finding 3

Most external benchmark issues are environment-related rather than algorithm-related.

------

## Finding 4

Local fallback smoke provides a reliable backup evaluation path.

------

# Limitation

Current implementation:

```text
AssertionError
→ unsupported_external_failure
```

Future work:

```text
assertion_failure
unittest_failure
pytest_failure
```

should be added as dedicated external failure categories.