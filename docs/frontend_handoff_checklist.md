# Frontend Handoff Checklist

## Public API Only

Frontends should import only:

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json
```

Do not call internal runners, tools, planners, appliers, or evaluators:

- `ShellTool`
- `PatchApplier`
- `PatchPlanner`
- `RepairBenchmarkRunner`
- `DiagnosisBenchmarkRunner`

## Legal run_task Calls

```python
controller.run_task(task_id, mode="diagnosis")
controller.run_task(task_id, mode="repair", confirm_apply=False)
controller.run_task(task_id, mode="repair", confirm_apply=True)
```

Do not use `diagnose`; the valid mode is `diagnosis`.

## Confirm Apply Semantics

The first repair run should use `confirm_apply=False`. If the stream emits
`PatchApprovalRequired`, show a confirmation control to the user.

When the user confirms, rerun the same task with:

```python
controller.run_task(task_id, mode="repair", confirm_apply=True)
```

The backend does not continue the same async generator after confirmation.

## Key UI Event Mapping

- `TaskStarted` -> task header/status
- `ErrorDetected` -> error card
- `FailureMemoryCreated` -> diagnosis/memory card
- `EnvRepairPlanCreated` -> environment/data repair card
- `PatchProposed` -> diff card
- `PatchReviewCreated` -> safety review card
- `PatchApprovalRequired` -> confirmation prompt
- `PatchApplied` -> patch application status
- `VerificationStarted` -> verification status
- `VerificationFinished` -> verification result
- `TaskFinished` -> final status

## EnvRepairPlanCreated

Show this as an environment/data repair card. It means the issue is not suitable
for a source-code patch. The backend will not install dependencies and will not
create missing files.

## PatchReviewCreated

Show this as a safety review card. If `blocked=True` or `approved=False`, do not
show Confirm Apply. A blocked patch will not be applied by the backend.

## Unknown Events

Unknown event types should not crash the frontend. Append them to a log panel so
new backend events remain forward-compatible.
