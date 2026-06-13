# m30_llm_smoke_results

# M30 Real LLM Smoke Results

## Objective

Evaluate real LLM integration using the SJTU Model Platform and compare three prompting modes.

Model:

```text
deepseek-chat
```

Provider:

```text
SJTU Model Platform
```

------

## Experimental Setup

Tasks:

```text
001 ~ 010
```

Modes:

```text
direct_llm
structured_patchplan
structured_patchplan_with_memory
```

Total Runs:

```text
10 × 3 = 30
```

------

## Results Summary

| Mode                             | Runs | API Success | Valid Output | Valid JSON | Reviewable | Patch Steps | Verification | Safety Review Field | Memory Field |
| -------------------------------- | ---- | ----------- | ------------ | ---------- | ---------- | ----------- | ------------ | ------------------- | ------------ |
| direct_llm                       | 10   | 10          | 10           | 0          | 0          | 0           | 10           | 0                   | 0            |
| structured_patchplan             | 10   | 10          | 10           | 10         | 10         | 10          | 10           | 10                  | 0            |
| structured_patchplan_with_memory | 10   | 10          | 10           | 10         | 10         | 10          | 10           | 10                  | 10           |

------

## Generated Artifacts

For every task and mode:

```text
prompt.txt
response.txt
summary.json
```

Saved under:

```text
outputs/m30_llm_smoke/
```

------

## Key Findings

### Direct LLM

Advantages:

- Successful API invocation
- Valid textual responses

Limitations:

- No structured JSON output
- No reviewable patch plan

------

### Structured PatchPlan

Advantages:

- Structured JSON output
- Reviewable repair plan
- Explicit patch steps

------

### Structured PatchPlan with Memory

Advantages:

- All structured patch plan capabilities
- Additional memory field
- Better support for future multi-step workflows

------

## Conclusion

All three modes achieved successful API execution.

However:

```text
Structured PatchPlan
```

and

```text
Structured PatchPlan with Memory
```

provide significantly better structured outputs than Direct LLM.