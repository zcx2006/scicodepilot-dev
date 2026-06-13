# Textual Frontend Update

## Summary

This update improves the existing Textual reference frontend for the SciCodePilot
internal benchmark demo. The original frontend could select a task, run
diagnosis or repair mode, and print backend events into a few log panels. The
updated version turns it into a clearer Agent execution dashboard for demo and
presentation use.

## Files Changed

- `scicodepilot/frontend/textual_app.py`
  - Main Textual UI implementation.
- `requirements.txt`
  - Adds basic runtime/test dependencies, including `textual`.
- `.gitignore`
  - Ignores Python cache files and generated frontend/workspace outputs.

## Main UI Changes

### 1. Execution Plan Tree

Added an `Execution Plan` tree in the center panel.

The tree shows the backend plan and current progress, for example:

```text
[x] 1. Run command
[x] 2. Parse failure
[x] 3. Build memory
[ ] 4. Generate patch
```

The backend does not emit `StepStarted` for every diagnosis sub-step, so the
frontend also advances the tree from event types:

- `CommandFinished` -> command step done
- `ErrorDetected` -> parse step done
- `FailureMemoryCreated` -> memory step done
- `TaskFinished` -> evaluation/final step done

This is frontend-only logic. The backend was not changed for this behavior.

### 2. Run Summary Panel

Added a right-side `Run Summary` panel that summarizes the current run:

```text
Task
Command
Error
Memory
Plan
Review
Apply
Verify
Final
Transcript
```

This makes screenshots and demos easier to explain without reading the full
event log.

### 3. Structured Event Panels

The right side is now organized around the project pipeline:

- `Diagnosis and Memory`
  - Error card
  - FailureMemory card
  - EnvRepairPlan card
- `Repair and Verification`
  - Plan card
  - Patch card
  - Safety review card
  - Confirmation card
  - Apply card
  - Verification card
  - Task summary card

This better matches the project idea:

```text
error -> FailureMemory -> PatchPlan / EnvRepairPlan -> review -> apply -> verify
```

### 4. Copyable Transcript Export

Textual terminal text is not always easy to select/copy. Each run now writes a
copyable transcript to:

```text
outputs/frontend_logs/
```

Example filename:

```text
20260613_015418_repair_collate_fn_009_diagnosis_transcript.txt
```

The transcript contains a readable event-by-event summary and can be shared in
reports, chat, or demo notes.

### 5. Visual Styling

Updated the UI styling:

- Three-column layout: controls, plan/timeline, structured results.
- Rounded panel borders.
- Unified blue panel borders.
- Orange section titles.
- Consistent panel backgrounds.
- Task and mode select boxes styled consistently.
- Status moved near the top of the left panel.

## How To Run

From the project root:

```powershell
cd C:\Users\user\Documents\scicodepilot\scicodepilot-dev
python scripts\run_textual_app.py
```

If dependencies are missing:

```powershell
pip install -r requirements.txt
```

Smoke test:

```powershell
python scripts\run_textual_app.py --smoke-test
```

## Current Backend Interface

The frontend still uses the existing public backend interface:

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict
```

Main calls:

```python
controller.list_tasks()
controller.run_task(task_id, mode, confirm_apply=False)
```

The frontend does not call internal repair/eval/tool modules directly.

## Current Scope

The UI currently supports the internal benchmark tasks under:

```text
benchmark/tasks/
```

It does not currently support arbitrary external repository paths or custom
commands from the UI. That would require a new backend public API such as:

```python
run_external_smoke(repo_path, command)
```

and an event stream compatible with the current frontend.

## Notes For Reviewers

- The original Textual frontend already existed.
- This update is a UI/UX and presentation-layer enhancement.
- The backend pipeline was not redesigned.
- The execution plan tree uses frontend event interpretation to compensate for
  diagnosis mode not emitting `StepStarted` for every logical stage.
- Generated logs are ignored through `.gitignore`.

