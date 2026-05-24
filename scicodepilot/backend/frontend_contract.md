# SciCodePilot Backend Frontend Contract

This document describes the stable backend entrypoint for the Textual frontend.
The frontend should treat `BackendController` as the recommended public API.

## Import

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json
```

## List Tasks

```python
controller = BackendController()
tasks = controller.list_tasks()
```

Each task is a `TaskInfo` model with:

- `task_id`
- `task_name`
- `category`
- `difficulty`
- `requires`

## Run Diagnosis

```python
async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="diagnosis",
):
    event_dict = event_to_dict(event)
```

## Run Repair Without Confirmation

This is the default safe repair mode. It proposes a patch and stops before
applying it.

```python
async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="repair",
    confirm_apply=False,
):
    event_dict = event_to_dict(event)
```

## Run Repair With Explicit Confirmation

Only use this path after the user explicitly approves applying the proposed
patch.

```python
async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="repair",
    confirm_apply=True,
):
    event_dict = event_to_dict(event)
```

## Event To UI Mapping

- `TaskStarted` -> title/status
- `PlanCreated` -> plan tree
- `StepStarted` -> active step
- `CommandStarted` -> log panel
- `CommandOutput` -> log panel
- `CommandFinished` -> command status
- `ErrorDetected` -> error card
- `FailureMemoryCreated` -> reflection/memory card
- `EnvRepairPlanCreated` -> environment/data repair card
- `PatchProposed` -> diff panel
- `PatchReviewCreated` -> patch safety review card
- `PatchApprovalRequired` -> permission prompt
- `PatchApplied` -> patch status
- `VerificationStarted` -> verification status
- `VerificationFinished` -> verification result
- `TaskFinished` -> final status

## Environment/Data Repair Plans

`EnvRepairPlanCreated` means the backend found a failure that is not a good
fit for a source-code patch. The user needs to take manual action such as
installing a dependency, downloading data, placing a missing config file, or
fixing a path/configuration.

The current backend only generates a structured plan. It does not automatically
install dependencies and does not create placeholder missing files.

## Patch Safety Review

Every `PatchProposed` event is followed by `PatchReviewCreated`. This event
represents a static safety review before confirmation or application. A blocked
patch will not enter confirmation, will not be applied, and will not run the
hidden evaluator.

The current reviewer is rule-based. It can be extended later with an LLM
reviewer while preserving the same event boundary.

## Recommended Frontend Boundary

The frontend should call:

- `BackendController`
- `event_to_dict`
- `event_to_json`

The frontend should not call internal tools directly:

- `ShellTool`
- `PatchApplier`
- `PatchPlanner`
- `RepairBenchmarkRunner`
- `DiagnosisBenchmarkRunner`

## Transport Note

The current backend API is an in-process `asyncio` event stream, not a WebSocket.
If SciCodePilot later needs a web frontend, a WebSocket wrapper can be added
around `BackendController.run_task(...)` without changing the core runners.

## Experimental LLM Planner Note

The optional LLM patch planner is currently exposed only through CLI flags for
backend experiments. The Textual public API does not expose `use_llm_planner`.
