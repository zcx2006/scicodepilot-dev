from __future__ import annotations

import asyncio
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, RichLog, Select, Static

from scicodepilot.backend.controller import BackendController, TaskInfo
from scicodepilot.backend.event_serializer import event_to_dict


class SciCodePilotTextualApp(App):
    """Minimal Textual app that consumes the BackendController event stream."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #main {
        height: 1fr;
    }

    #controls {
        width: 34;
        padding: 1;
        border: solid $accent;
    }

    #log-panel {
        width: 1fr;
        border: solid $primary;
    }

    #side-panel {
        width: 1fr;
    }

    .panel {
        height: 1fr;
        border: solid $secondary;
        padding: 1;
    }

    Select, Button {
        width: 100%;
        margin-bottom: 1;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, controller: BackendController | None = None) -> None:
        super().__init__()
        self.controller = controller or BackendController()
        self.tasks: list[TaskInfo] = self.controller.list_tasks()
        self.selected_task_id = self.tasks[0].task_id if self.tasks else ""
        self.selected_mode = "diagnosis"
        self._run_task: asyncio.Task[None] | None = None

    def compose(self) -> ComposeResult:
        task_options = [
            (task.task_id, task.task_id)
            for task in self.tasks
        ] or [("No benchmark tasks found", "")]

        yield Header(show_clock=True)
        with Horizontal(id="main"):
            with Vertical(id="controls"):
                yield Static("Task")
                yield Select(
                    task_options,
                    value=self.selected_task_id,
                    id="task-select",
                    allow_blank=False,
                )
                yield Static("Mode")
                yield Select(
                    [("diagnosis", "diagnosis"), ("repair", "repair")],
                    value="diagnosis",
                    id="mode-select",
                    allow_blank=False,
                )
                yield Button("Run", id="run-button", variant="primary")
                yield Button(
                    "Confirm Apply",
                    id="confirm-apply-button",
                    variant="warning",
                    disabled=True,
                )
                yield Static(
                    "Ready.",
                    id="status-text",
                )
            yield RichLog(id="log-panel", wrap=True, markup=False, highlight=True)
            with Vertical(id="side-panel"):
                yield RichLog(
                    id="error-memory-panel",
                    classes="panel",
                    wrap=True,
                    markup=False,
                    highlight=True,
                )
                yield RichLog(
                    id="patch-verification-panel",
                    classes="panel",
                    wrap=True,
                    markup=False,
                    highlight=True,
                )
        yield Footer()

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "task-select":
            self.selected_task_id = str(event.value)
        elif event.select.id == "mode-select":
            self.selected_mode = str(event.value)
            if self.selected_mode == "diagnosis":
                self._confirm_button.disabled = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-button":
            await self._start_run(
                task_id=self.selected_task_id,
                mode=self.selected_mode,
                confirm_apply=False,
            )
        elif event.button.id == "confirm-apply-button":
            await self._start_run(
                task_id=self.selected_task_id,
                mode="repair",
                confirm_apply=True,
            )

    async def _start_run(
        self,
        task_id: str,
        mode: str,
        confirm_apply: bool,
    ) -> None:
        if not task_id:
            self._status.update("No task selected.")
            return
        if self._run_task is not None and not self._run_task.done():
            self._status.update("A task is already running.")
            return

        self.selected_mode = mode
        self._clear_panels()
        self._run_button.disabled = True
        self._confirm_button.disabled = True
        self._status.update(
            f"Running {task_id} in {mode}"
            + (" with confirmation." if confirm_apply else ".")
        )
        self._run_task = asyncio.create_task(
            self._consume_events(task_id, mode, confirm_apply)
        )

    async def _consume_events(
        self,
        task_id: str,
        mode: str,
        confirm_apply: bool,
    ) -> None:
        try:
            async for event in self.controller.run_task(
                task_id=task_id,
                mode=mode,
                confirm_apply=confirm_apply,
            ):
                event_dict = event_to_dict(event)
                self._handle_event(event_dict)
        except Exception as exc:
            self._log_panel.write(f"Frontend run failed: {exc}")
            self._status.update("Run failed.")
        finally:
            self._run_button.disabled = False

    def _handle_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type", "UnknownEvent")

        if event_type in {"CommandStarted", "CommandOutput", "CommandFinished"}:
            self._write_command_event(event)
            return

        if event_type in {
            "ErrorDetected",
            "FailureMemoryCreated",
            "EnvRepairPlanCreated",
        }:
            self._write_error_memory_event(event)
            return

        if event_type in {
            "PatchProposed",
            "PatchReviewCreated",
            "PatchApprovalRequired",
            "PatchApplied",
            "VerificationStarted",
            "VerificationFinished",
            "TaskFinished",
        }:
            self._write_patch_verification_event(event)
            return

        if event_type in {"TaskStarted", "PlanCreated", "StepStarted"}:
            self._write_status_event(event)
            return

        self._log_panel.write(f"Unknown event: {event}")

    def _write_command_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "CommandStarted":
            self._log_panel.write(f"$ {event.get('command')}")
        elif event_type == "CommandOutput":
            stream = event.get("stream")
            content = event.get("content")
            self._log_panel.write(f"{stream}: {content}")
        elif event_type == "CommandFinished":
            self._log_panel.write(
                "Command finished "
                f"return_code={event.get('return_code')} "
                f"success={event.get('success')}"
            )

    def _write_error_memory_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "ErrorDetected":
            self._error_memory.write(
                f"ErrorDetected: {event.get('error_type')}\n"
                f"{event.get('summary')}\n"
                f"Evidence: {event.get('evidence')}"
            )
        elif event_type == "FailureMemoryCreated":
            self._error_memory.write(
                "FailureMemoryCreated\n"
                f"Root cause: {event.get('root_cause_hypothesis')}\n"
                f"Repair action: {event.get('repair_action')}"
            )
        elif event_type == "EnvRepairPlanCreated":
            actions = "\n".join(
                f"- {action}" for action in event.get("suggested_actions", [])
            )
            self._error_memory.write(
                "EnvRepairPlanCreated\n"
                f"Category: {event.get('issue_category')}\n"
                f"{event.get('summary')}\n"
                f"Requires user action: {event.get('requires_user_action')}\n"
                f"Actions:\n{actions}"
            )

    def _write_patch_verification_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "PatchProposed":
            self._patch_verification.write(
                "PatchProposed\n"
                f"Target: {event.get('target_file')}\n"
                f"Confidence: {event.get('confidence')}\n"
                f"{event.get('unified_diff')}"
            )
        elif event_type == "PatchReviewCreated":
            self._patch_verification.write(
                "PatchReviewCreated\n"
                f"approved={event.get('approved')} "
                f"blocked={event.get('blocked')} "
                f"risk={event.get('risk_level')}\n"
                f"Reasons: {event.get('reasons')}\n"
                f"Warnings: {event.get('warnings')}"
            )
        elif event_type == "PatchApprovalRequired":
            self._confirm_button.disabled = False
            self._patch_verification.write(
                "PatchApprovalRequired\n"
                f"{event.get('message')}"
            )
        elif event_type == "PatchApplied":
            self._patch_verification.write(
                "PatchApplied\n"
                f"success={event.get('success')}\n"
                f"{event.get('message')}"
            )
        elif event_type == "VerificationStarted":
            self._patch_verification.write(
                f"VerificationStarted\n$ {event.get('command')}"
            )
        elif event_type == "VerificationFinished":
            self._patch_verification.write(
                "VerificationFinished\n"
                f"success={event.get('success')} "
                f"return_code={event.get('return_code')}\n"
                f"{event.get('summary')}"
            )
        elif event_type == "TaskFinished":
            self._patch_verification.write(
                "TaskFinished\n"
                f"status={event.get('status')}\n"
                f"{event.get('summary')}"
            )
            self._status.update(f"Finished: {event.get('status')}")
            self._run_button.disabled = False

    def _write_status_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "TaskStarted":
            self._status.update(f"Started: {event.get('task_id')}")
        elif event_type == "PlanCreated":
            steps = "\n".join(f"{index + 1}. {step}" for index, step in enumerate(event.get("steps", [])))
            self._patch_verification.write(f"PlanCreated\n{steps}")
        elif event_type == "StepStarted":
            self._status.update(
                f"Step {event.get('step_index')}: {event.get('step_name')}"
            )

    def _clear_panels(self) -> None:
        self._log_panel.clear()
        self._error_memory.clear()
        self._patch_verification.clear()

    @property
    def _run_button(self) -> Button:
        return self.query_one("#run-button", Button)

    @property
    def _confirm_button(self) -> Button:
        return self.query_one("#confirm-apply-button", Button)

    @property
    def _status(self) -> Static:
        return self.query_one("#status-text", Static)

    @property
    def _log_panel(self) -> RichLog:
        return self.query_one("#log-panel", RichLog)

    @property
    def _error_memory(self) -> RichLog:
        return self.query_one("#error-memory-panel", RichLog)

    @property
    def _patch_verification(self) -> RichLog:
        return self.query_one("#patch-verification-panel", RichLog)
