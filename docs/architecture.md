# SciCodePilot Architecture

SciCodePilot is a backend for a small scientific-code diagnosis and repair
benchmark. It runs benchmark tasks, emits structured events, proposes safe
source-code patches when appropriate, and keeps original benchmark repos
unchanged.

## Pipeline

```text
BackendController
  |
  +-- diagnosis mode
  |     run command in isolated workspace
  |     -> TracebackParser
  |     -> FailureMemoryBuilder
  |     -> optional diagnosis evaluator
  |     -> event stream
  |
  +-- repair mode
        run command in isolated workspace
        -> TracebackParser
        -> FailureMemoryBuilder
        -> PatchPlanner or optional LLMPatchPlanner
        -> EnvDoctor when no source patch is appropriate
        -> PatchSafetyReviewer
        -> PatchApprovalRequired
        -> PatchApplier in workspace only
        -> verification
        -> HiddenEvaluator writes score.json
        -> event stream
```

## Public API

Frontends should depend only on:

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json
```

`BackendController` exposes:

- `list_tasks()`
- `get_task(task_id)`
- `run_task(task_id, mode, confirm_apply=False)`

Valid modes are `diagnosis` and `repair`.

## Event Stream

The backend emits structured events such as `TaskStarted`, `ErrorDetected`,
`FailureMemoryCreated`, `EnvRepairPlanCreated`, `PatchProposed`,
`PatchReviewCreated`, `PatchApprovalRequired`, `PatchApplied`,
`VerificationFinished`, and `TaskFinished`.

Frontends should convert each event with `event_to_dict(event)` and update UI
incrementally. Unknown events should be logged rather than treated as fatal.

## Diagnosis vs Repair

Diagnosis mode runs the task and explains the failure. Repair mode runs the
same diagnosis path, then attempts to create a source-code patch when the error
class supports it.

For repair mode, `confirm_apply=False` proposes a patch and stops at approval.
`confirm_apply=True` reruns the task, proposes and reviews the patch again, then
applies it in the isolated workspace if approved.

## Workspace Isolation

Repairs and evaluation run under:

```text
outputs/workspaces/<run_id>/<task_id>/repo
```

The original `benchmark/tasks/*/repo` directories are not patched. This keeps
benchmark bugs stable for repeated demos and tests.

## Hidden Evaluator and score.json

The hidden evaluator is a minimal evaluator for this benchmark. It writes
`score.json` for successful repair workflows in the workspace. It should not be
described as a full hidden test suite; it is currently a compact scoring
boundary for these benchmark tasks.

## EnvDoctor

`EnvDoctor` handles `missing_module` and `missing_file`. These are dependency,
environment, data, or configuration issues rather than source-code patch
targets. It emits `EnvRepairPlanCreated` with suggested user actions. It does
not run `pip install`, does not run `conda install`, and does not create missing
files.

## LLM Planner

The optional LLM planner is disabled by default. When enabled from CLI, it can
use `mock`, `deepseek`, `gemini`, `openai`, or `disabled` providers. It only
generates a `PatchPlan`. It does not modify files, run shell commands, install
dependencies, or bypass safety review.

If the LLM provider is not configured, has no API key, fails, returns invalid
JSON, or returns an unusable patch, the repair runner falls back to the
deterministic rule-based `PatchPlanner`.

## PatchSafetyReviewer

Every `PatchPlan`, whether rule-based or LLM-generated, is reviewed before
confirmation or application. The rule-based reviewer blocks empty diffs,
absolute paths, path traversal, blocked project areas, dangerous command-like
content, and multi-file diffs. It emits `PatchReviewCreated`.

Blocked patches do not reach `PatchApprovalRequired`, are not applied, and do
not run the hidden evaluator.

## Textual Reference Frontend

The Textual app is a reference frontend that demonstrates how to consume the
event stream. It is not the only intended UI. Other frontends should follow the
same public API and event contract.
