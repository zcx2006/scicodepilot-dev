# Failure Taxonomy

## Supported Error Types

| Error Type | Evidence Source | Main Handling Modules | Boundary |
| --- | --- | --- | --- |
| `tensor_shape` | PyTorch shape RuntimeError stderr | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple dimension constant repairs such as 64/128 mismatch. |
| `dtype_mismatch` | PyTorch dtype RuntimeError stderr | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple float32/float64 source-code mismatch. |
| `device_mismatch` | RuntimeError stderr mentioning incompatible devices | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple CPU/CUDA placement alignment. |
| `loss_input_error` | loss contract ValueError stderr | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple target kind preparation errors for classification loss. |
| `missing_module` | ModuleNotFoundError stderr | TracebackParser, FailureMemoryBuilder, EnvDoctor | Produces environment/dependency plan; does not install packages. |
| `missing_file` | FileNotFoundError stderr | TracebackParser, FailureMemoryBuilder, EnvDoctor | Produces data/config plan; does not create files. |
| `entrypoint_error` | NameError stderr for `mainn` | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple misspelled entrypoint. |
| `label_shape` | PyTorch loss batch-size RuntimeError stderr | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple label batch-size mismatch. |
| `collate_fn_error` | KeyError stderr mentioning collate_fn batch structure | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple batch key mismatch between collate_fn and train loop. |
| `config_key_error` | KeyError stderr mentioning experiment config key | TracebackParser, FailureMemoryBuilder, PatchPlanner, PatchSafetyReviewer | Handles simple misspelled config key lookup. |

## Module Roles

- TracebackParser extracts an error type and evidence from stderr.
- FailureMemoryBuilder converts parsed errors into reusable explanation and
  repair-action text.
- PatchPlanner proposes deterministic source-code patches for supported source
  repair tasks.
- EnvDoctor routes environment and data issues to EnvRepairPlanCreated.
- PatchSafetyReviewer checks every PatchPlan before confirmation or apply.

## Possible Failure Modes

- Parser misses unfamiliar stderr wording.
- Rule-based PatchPlanner cannot localize a new code pattern.
- EnvDoctor may identify that user action is required but cannot fetch data or
  install dependencies.
- LLM planner may return invalid JSON or unsafe diffs; these fall back or are
  blocked.
- PatchSafetyReviewer is static and conservative; it may block unusual but safe
  patches, or warn on weak alignment.
