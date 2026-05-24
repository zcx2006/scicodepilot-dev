# Results Analysis

## Main 10-task Result

The current benchmark contains 10 tasks: 8 source-code repair tasks and 2
environment/data diagnosis tasks.

Full system expected result:

- 10/10 diagnosis successes
- 8/8 source-code repairs after confirmation
- 2/2 environment/data failures routed to EnvDoctor
- `average_score=1.0`

The source-code repairs cover tensor shape, dtype mismatch, device mismatch,
loss input preparation, collate function structure, config key mismatch,
entrypoint typo, and label shape mismatch. The env/data tasks cover missing
module and missing file failures.

## Mock LLM Result

The mock LLM planner reaches the same repair score as the rule-based planner on
the benchmark, while still passing through PatchReviewCreated. This does not
claim real provider superiority. It demonstrates that optional LLM planning can
be attached without bypassing the safety gate.

## SafetyReviewer Result

The safety stress cases exercise blocked target paths, path traversal,
dependency-install commands, destructive shell terms, Python shell execution
terms, and multi-file diffs. Passing these cases supports the claim that
PatchSafetyReviewer can stop dangerous patches before confirmation or apply.

## Benchmark Limitations

- The task count is still small.
- The hidden evaluator is lightweight and primarily checks command success and
  score.json generation.
- The rule-based planner is intentionally targeted to the current error modes.
- The benchmark does not yet include large, real-world scientific repositories.

## Why The Results Still Matter

These limitations do not erase the course-project value. SciCodePilot provides a
controlled benchmark, a reproducible evaluation protocol, a transparent event
stream, clear routing between source repair and env/data plans, workspace
isolation, and an explicit safety boundary before patch application.
