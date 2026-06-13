from __future__ import annotations

import asyncio
import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, RichLog, Select, Static, Tree

from scicodepilot.backend.controller import BackendController, TaskInfo
from scicodepilot.backend.event_serializer import event_to_dict


class SciCodePilotTextualApp(App):
    """Reference Textual frontend for the SciCodePilot event stream."""

    CSS = """
    * {
        scrollbar-size: 1 1;
        scrollbar-size-horizontal: 1;
        scrollbar-size-vertical: 1;
    }

    RichLog, Tree, VerticalScroll {
        scrollbar-size: 1 1;
        scrollbar-size-horizontal: 1;
        scrollbar-size-vertical: 1;
    }

    Screen {
        layout: vertical;
        scrollbar-size: 1 1;
        background: $surface;
    }

    Header {
        background: $primary;
    }

    #main {
        height: 1fr;
        align: left top;
        background: $surface;
    }

    #controls {
        width: 38;
        height: 1fr;
        padding: 1;
        border: round $primary;
        background: $surface;
        scrollbar-size: 1 1;
    }

    #center-panel {
        width: 1fr;
        height: 1fr;
        scrollbar-size: 1 1;
        background: $surface;
    }

    #phase-strip {
        height: 13;
        border: round $primary;
        padding: 1;
        background: $surface;
        scrollbar-size: 1 1;
        scrollbar-size-horizontal: 1;
        scrollbar-size-vertical: 1;
    }

    #timeline-panel {
        height: 1fr;
        border: round $primary;
        padding: 0 1;
        background: $surface;
        scrollbar-size: 1 1;
        scrollbar-size-horizontal: 1;
        scrollbar-size-vertical: 1;
    }

    #side-panel {
        width: 56;
        height: 1fr;
        scrollbar-size: 1 1;
        background: $surface;
    }

    .panel {
        height: 1fr;
        border: round $primary;
        padding: 1;
        background: $surface;
        scrollbar-size: 1 1;
        scrollbar-size-horizontal: 1;
        scrollbar-size-vertical: 1;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-left: 1;
        padding: 0 1;
        background: $surface;
        height: 1;
    }

    #app-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #task-details {
        min-height: 7;
        padding: 1;
        border: round $primary;
        background: $surface;
        margin-bottom: 1;
    }

    #status-text {
        min-height: 8;
        padding: 1;
        border: round $primary;
        background: $surface;
    }

    #summary-panel {
        height: 11;
        border: round $primary;
        padding: 1;
        background: $surface;
        scrollbar-size: 1 1;
        scrollbar-size-horizontal: 1;
        scrollbar-size-vertical: 1;
    }

    Select, Button {
        width: 100%;
        margin-bottom: 1;
    }

    Select {
        border: round $primary;
        background: $surface;
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
        self._run_log_path: Path | None = None
        self._transcript_path: Path | None = None
        self._event_count = 0
        self._run_summary: dict[str, str] = {}
        self._plan_steps: list[str] = []
        self._plan_states: list[str] = []
        self._phase_state: dict[str, str] = {
            "run": "idle",
            "diagnose": "idle",
            "plan": "idle",
            "review": "idle",
            "apply": "idle",
            "verify": "idle",
        }

    def compose(self) -> ComposeResult:
        task_options = [
            (self._task_option_label(task), task.task_id)
            for task in self.tasks
        ] or [("No benchmark tasks found", "")]

        yield Header(show_clock=True)
        with Horizontal(id="main"):
            with VerticalScroll(id="controls"):
                yield Static("SciCodePilot Console", id="app-title")
                yield Static("Status", classes="section-title")
                yield Static(
                    "Ready.",
                    id="status-text",
                )
                yield Static("Task", classes="section-title")
                yield Select(
                    task_options,
                    value=self.selected_task_id,
                    id="task-select",
                    allow_blank=False,
                )
                yield Static("", id="task-details")
                yield Static("Mode", classes="section-title")
                yield Select(
                    [
                        ("Diagnosis only", "diagnosis"),
                        ("Repair proposal", "repair"),
                    ],
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
            with Vertical(id="center-panel"):
                yield Static("Execution Plan", classes="section-title")
                yield Tree("Plan", id="phase-strip")
                yield Static("Timeline", classes="section-title")
                yield RichLog(
                    id="timeline-panel",
                    wrap=True,
                    markup=False,
                    highlight=True,
                )
            with Vertical(id="side-panel"):
                yield Static("Run Summary", classes="section-title")
                yield RichLog(
                    id="summary-panel",
                    wrap=True,
                    markup=False,
                    highlight=True,
                )
                yield Static("Diagnosis and Memory", classes="section-title")
                yield RichLog(
                    id="diagnosis-panel",
                    classes="panel",
                    wrap=True,
                    markup=False,
                    highlight=True,
                )
                yield Static("Repair and Verification", classes="section-title")
                yield RichLog(
                    id="repair-panel",
                    classes="panel",
                    wrap=True,
                    markup=False,
                    highlight=True,
                )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "SciCodePilot"
        self.sub_title = "Structured Scientific-Code Repair"
        self._update_task_details()
        self._render_phase_strip()
        self._clear_panels()

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "task-select":
            self.selected_task_id = str(event.value)
            self._update_task_details()
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
        self._event_count = 0
        self._reset_run_summary()
        self._start_run_log(task_id, mode, confirm_apply)
        self._reset_phase_state()
        self._run_button.disabled = True
        self._confirm_button.disabled = True
        self._status.update(
            f"Running {task_id}\nmode={mode}"
            + (" with confirmation." if confirm_apply else ".")
            + f"\ntranscript={self._transcript_name()}"
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
                self._event_count += 1
                self._handle_event(event_dict)
        except Exception as exc:
            self._timeline.write(f"[frontend] run failed: {exc}")
            self._status.update("Run failed.")
        finally:
            self._run_button.disabled = False

    def _handle_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type", "UnknownEvent")
        self._append_run_log("event", json.dumps(event, ensure_ascii=False))
        self._timeline.write(self._timeline_line(event))

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

        self._timeline.write(f"Unknown event payload: {event}")

    def _write_command_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "CommandStarted":
            self._mark_phase("run", "active")
            self._set_logical_step("command", "active")
            self._timeline.write(f"$ {event.get('command')}")
        elif event_type == "CommandOutput":
            stream = event.get("stream")
            content = event.get("content")
            self._timeline.write(self._wrap_block(f"{stream}: {content}", width=38))
        elif event_type == "CommandFinished":
            self._mark_phase("run", "done" if event.get("success") else "failed")
            self._set_logical_step("command", "done")
            self._run_summary["command"] = (
                "passed" if event.get("success") else "failed"
            )
            self._render_summary()
            self._timeline.write(
                self._wrap_block(
                    "Command finished "
                    f"return_code={event.get('return_code')} "
                    f"success={event.get('success')}",
                    width=38,
                )
            )

    def _write_error_memory_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "ErrorDetected":
            self._mark_phase("diagnose", "active")
            self._set_logical_step("parse", "done")
            self._run_summary["error"] = str(event.get("error_type"))
            self._render_summary()
            self._diagnosis.write(
                self._card(
                    "Error Card",
                    [
                        f"Type: {event.get('error_type')}",
                        f"Summary: {event.get('summary')}",
                        "Evidence:",
                        self._format_list(event.get("evidence", [])),
                    ],
                )
            )
        elif event_type == "FailureMemoryCreated":
            self._mark_phase("diagnose", "done")
            self._set_logical_step("memory", "done")
            self._run_summary["memory"] = "created"
            self._render_summary()
            self._diagnosis.write(
                self._card(
                    "FailureMemory Card",
                    [
                        f"Error type: {event.get('error_type')}",
                        f"Root cause: {event.get('root_cause_hypothesis')}",
                        f"Repair action: {event.get('repair_action')}",
                    ],
                )
            )
        elif event_type == "EnvRepairPlanCreated":
            self._mark_phase("plan", "done")
            self._set_logical_step("plan", "done")
            self._set_logical_step("apply", "skipped")
            self._set_logical_step("verify", "skipped")
            self._mark_phase("review", "skipped")
            self._mark_phase("apply", "skipped")
            self._mark_phase("verify", "skipped")
            self._run_summary["plan"] = "env/data repair"
            self._run_summary["review"] = "skipped"
            self._run_summary["apply"] = "skipped"
            self._run_summary["verify"] = "skipped"
            self._render_summary()
            self._diagnosis.write(
                self._card(
                    "EnvRepairPlan Card",
                    [
                        f"Category: {event.get('issue_category')}",
                        f"Summary: {event.get('summary')}",
                        f"Requires user action: {event.get('requires_user_action')}",
                        "Actions:",
                        self._format_list(event.get("suggested_actions", [])),
                    ],
                )
            )

    def _write_patch_verification_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "PatchProposed":
            self._mark_phase("plan", "done")
            self._set_logical_step("plan", "done")
            self._run_summary["plan"] = "patch proposed"
            self._render_summary()
            self._repair.write(
                self._card(
                    "Patch Card",
                    [
                        f"Target: {event.get('target_file')}",
                        f"Confidence: {event.get('confidence')}",
                        f"Change: {event.get('proposed_change')}",
                        "Diff:",
                        self._format_diff(str(event.get("unified_diff", ""))),
                    ],
                )
            )
        elif event_type == "PatchReviewCreated":
            blocked = bool(event.get("blocked"))
            approved = bool(event.get("approved"))
            self._mark_phase("review", "failed" if blocked else "done")
            self._run_summary["review"] = (
                "blocked" if blocked else "approved" if approved else "not approved"
            )
            if not approved or blocked:
                self._mark_phase("apply", "skipped")
                self._mark_phase("verify", "skipped")
                self._run_summary["apply"] = "skipped"
                self._run_summary["verify"] = "skipped"
            self._render_summary()
            self._repair.write(
                self._card(
                    "Safety Review Card",
                    [
                        f"Approved: {event.get('approved')}",
                        f"Blocked: {event.get('blocked')}",
                        f"Risk: {event.get('risk_level')}",
                        "Reasons:",
                        self._format_list(event.get("reasons", [])),
                        "Warnings:",
                        self._format_list(event.get("warnings", [])),
                    ],
                )
            )
        elif event_type == "PatchApprovalRequired":
            self._confirm_button.disabled = False
            self._mark_phase("apply", "waiting")
            self._set_logical_step("apply", "waiting")
            self._run_summary["apply"] = "awaiting confirmation"
            self._render_summary()
            self._repair.write(
                self._card(
                    "Confirmation Card",
                    [
                        str(event.get("message")),
                        f"Target: {event.get('target_file')}",
                    ],
                )
            )
        elif event_type == "PatchApplied":
            self._mark_phase("apply", "done" if event.get("success") else "failed")
            self._set_logical_step("apply", "done" if event.get("success") else "failed")
            self._run_summary["apply"] = (
                "applied" if event.get("success") else "failed"
            )
            self._render_summary()
            self._repair.write(
                self._card(
                    "Apply Card",
                    [
                        f"Success: {event.get('success')}",
                        f"Message: {event.get('message')}",
                    ],
                )
            )
        elif event_type == "VerificationStarted":
            self._mark_phase("verify", "active")
            self._set_logical_step("verify", "active")
            self._repair.write(
                f"VerificationStarted\n$ {event.get('command')}"
            )
        elif event_type == "VerificationFinished":
            self._mark_phase("verify", "done" if event.get("success") else "failed")
            self._set_logical_step("verify", "done" if event.get("success") else "failed")
            self._run_summary["verify"] = (
                "passed" if event.get("success") else "failed"
            )
            self._render_summary()
            self._repair.write(
                self._card(
                    "Verification Card",
                    [
                        f"Success: {event.get('success')}",
                        f"Return code: {event.get('return_code')}",
                        f"Summary: {event.get('summary')}",
                    ],
                )
            )
        elif event_type == "TaskFinished":
            self._finish_plan_for_task(event)
            self._run_summary["final"] = str(event.get("status"))
            self._render_summary()
            self._repair.write(
                self._card(
                    "Task Summary Card",
                    [
                        f"Status: {event.get('status')}",
                        f"Summary: {event.get('summary')}",
                    ],
                )
            )
            self._status.update(
                f"Finished: {event.get('status')}\n"
                f"events={self._event_count}\n"
                f"transcript={self._transcript_name()}\n"
                "folder=outputs/frontend_logs"
            )
            self._run_button.disabled = False

    def _write_status_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "TaskStarted":
            self._mark_phase("run", "active")
            self._run_summary["task"] = str(event.get("task_id"))
            self._render_summary()
            self._status.update(f"Started: {event.get('task_id')}")
        elif event_type == "PlanCreated":
            self._render_plan_tree(event.get("steps", []))
            self._repair.write(
                self._card(
                    "Plan Card",
                    [
                        "Steps:",
                        self._format_list(event.get("steps", [])),
                    ],
                )
            )
        elif event_type == "StepStarted":
            self._activate_plan_step(int(event.get("step_index", 0)))
            self._status.update(
                f"Step {event.get('step_index')}: {event.get('step_name')}"
            )

    def _clear_panels(self) -> None:
        self._timeline.clear()
        self._summary.clear()
        self._diagnosis.clear()
        self._repair.clear()
        self._timeline.write("Timeline\nWaiting for backend events.")
        self._summary.write("Run Summary\nNo run started yet.")
        self._diagnosis.write("Diagnosis and Memory\nNo failure analyzed yet.")
        self._repair.write("Repair and Verification\nNo patch proposed yet.")

    def _start_run_log(
        self,
        task_id: str,
        mode: str,
        confirm_apply: bool,
    ) -> None:
        log_dir = Path("outputs") / "frontend_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._run_log_path = (log_dir / f"{timestamp}_{task_id}_{mode}.log").resolve()
        self._transcript_path = (
            log_dir / f"{timestamp}_{task_id}_{mode}_transcript.txt"
        ).resolve()
        self._run_log_path.write_text(
            "SciCodePilot frontend run log\n"
            f"task_id={task_id}\n"
            f"mode={mode}\n"
            f"confirm_apply={confirm_apply}\n\n",
            encoding="utf-8",
        )
        self._transcript_path.write_text(
            "SciCodePilot Copyable Transcript\n"
            f"Task: {task_id}\n"
            f"Mode: {mode}\n"
            f"Confirm apply: {confirm_apply}\n\n",
            encoding="utf-8",
        )

    def _append_run_log(self, section: str, message: str) -> None:
        if self._run_log_path is None:
            return
        with self._run_log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{section}] {message}\n")
        if self._transcript_path is not None and section == "event":
            event = json.loads(message)
            with self._transcript_path.open("a", encoding="utf-8") as transcript:
                transcript.write(self._copyable_event_text(event))
                transcript.write("\n")

    def _copyable_event_text(self, event: dict[str, Any]) -> str:
        event_type = event.get("type", "UnknownEvent")
        header = self._timeline_line(event)

        if event_type == "CommandStarted":
            return f"{header}\nCommand: {event.get('command')}\n"
        if event_type == "CommandOutput":
            return (
                f"{header}\n"
                f"{event.get('stream')}: {event.get('content')}\n"
            )
        if event_type == "CommandFinished":
            return (
                f"{header}\n"
                f"Return code: {event.get('return_code')}\n"
                f"Success: {event.get('success')}\n"
            )
        if event_type == "ErrorDetected":
            return (
                f"{header}\n"
                f"Error type: {event.get('error_type')}\n"
                f"Summary: {event.get('summary')}\n"
                f"Evidence:\n{self._format_list(event.get('evidence', []))}\n"
            )
        if event_type == "FailureMemoryCreated":
            return (
                f"{header}\n"
                f"Error type: {event.get('error_type')}\n"
                f"Root cause: {event.get('root_cause_hypothesis')}\n"
                f"Repair action: {event.get('repair_action')}\n"
            )
        if event_type == "EnvRepairPlanCreated":
            return (
                f"{header}\n"
                f"Category: {event.get('issue_category')}\n"
                f"Summary: {event.get('summary')}\n"
                f"Requires user action: {event.get('requires_user_action')}\n"
                f"Actions:\n{self._format_list(event.get('suggested_actions', []))}\n"
            )
        if event_type == "PatchProposed":
            return (
                f"{header}\n"
                f"Target: {event.get('target_file')}\n"
                f"Confidence: {event.get('confidence')}\n"
                f"Change: {event.get('proposed_change')}\n"
                f"Diff:\n{event.get('unified_diff')}\n"
            )
        if event_type == "PatchReviewCreated":
            return (
                f"{header}\n"
                f"Approved: {event.get('approved')}\n"
                f"Blocked: {event.get('blocked')}\n"
                f"Risk: {event.get('risk_level')}\n"
                f"Reasons:\n{self._format_list(event.get('reasons', []))}\n"
                f"Warnings:\n{self._format_list(event.get('warnings', []))}\n"
            )
        if event_type == "PatchApprovalRequired":
            return f"{header}\n{event.get('message')}\n"
        if event_type == "PatchApplied":
            return (
                f"{header}\n"
                f"Success: {event.get('success')}\n"
                f"Message: {event.get('message')}\n"
            )
        if event_type == "VerificationStarted":
            return f"{header}\nVerification command: {event.get('command')}\n"
        if event_type == "VerificationFinished":
            return (
                f"{header}\n"
                f"Success: {event.get('success')}\n"
                f"Return code: {event.get('return_code')}\n"
                f"Summary: {event.get('summary')}\n"
            )
        if event_type == "TaskFinished":
            return (
                f"{header}\n"
                f"Status: {event.get('status')}\n"
                f"Summary: {event.get('summary')}\n"
            )

        return f"{header}\nPayload: {json.dumps(event, ensure_ascii=False)}\n"

    def _task_option_label(self, task: TaskInfo) -> str:
        return f"{task.task_id} | {task.category} | {task.difficulty}"

    def _selected_task(self) -> TaskInfo | None:
        return next(
            (task for task in self.tasks if task.task_id == self.selected_task_id),
            None,
        )

    def _update_task_details(self) -> None:
        task = self._selected_task()
        if task is None:
            self._task_details.update("No task selected.")
            return

        requires = ", ".join(task.requires) if task.requires else "none"
        self._task_details.update(
            f"{task.task_name}\n"
            f"id={task.task_id}\n"
            f"category={task.category}\n"
            f"difficulty={task.difficulty}\n"
            f"requires={requires}"
        )

    def _reset_phase_state(self) -> None:
        self._plan_steps = []
        self._plan_states = []
        for key in self._phase_state:
            self._phase_state[key] = "idle"
        self._render_phase_strip()

    def _mark_phase(self, phase: str, state: str) -> None:
        self._phase_state[phase] = state
        if not self._plan_steps:
            self._render_phase_strip()

    def _render_phase_strip(self) -> None:
        self._render_default_plan_tree()

    def _render_default_plan_tree(self) -> None:
        labels = {
            "run": "Run",
            "diagnose": "Diagnose",
            "plan": "Plan",
            "review": "Review",
            "apply": "Apply",
            "verify": "Verify",
        }
        root = self._phase_strip.root
        root.remove_children()
        for key, label in labels.items():
            root.add(f"{self._state_icon(self._phase_state[key])} {label}")
        self._phase_strip.root.expand()

    def _render_plan_tree(self, steps: list[Any]) -> None:
        self._plan_steps = [str(step) for step in steps]
        self._plan_states = ["idle" for _ in self._plan_steps]
        root = self._phase_strip.root
        root.remove_children()
        self._redraw_plan_tree()
        self._phase_strip.root.expand()

    def _activate_plan_step(self, step_index: int) -> None:
        if not self._plan_steps:
            return
        for index in range(1, min(step_index, len(self._plan_states))):
            if self._plan_states[index - 1] in {"idle", "active"}:
                self._plan_states[index - 1] = "done"
        if 1 <= step_index <= len(self._plan_states):
            self._plan_states[step_index - 1] = "active"
        self._redraw_plan_tree()

    def _set_plan_step(self, step_index: int, state: str) -> None:
        if not self._plan_steps or not 1 <= step_index <= len(self._plan_states):
            return
        if state == "done":
            for index in range(1, step_index):
                if self._plan_states[index - 1] in {"idle", "active"}:
                    self._plan_states[index - 1] = "done"
        self._plan_states[step_index - 1] = state
        self._redraw_plan_tree()

    def _set_logical_step(self, logical_step: str, state: str) -> None:
        if not self._plan_steps:
            return
        step_index = self._logical_step_index(logical_step)
        if step_index is not None:
            self._set_plan_step(step_index, state)

    def _logical_step_index(self, logical_step: str) -> int | None:
        mode_map = {
            "diagnosis": {
                "command": 2,
                "parse": 3,
                "memory": 4,
                "evaluate": 5,
            },
            "repair": {
                "command": 1,
                "parse": 2,
                "memory": 3,
                "plan": 4,
                "apply": 5,
                "verify": 6,
                "restore": 7,
            },
        }
        return mode_map.get(self.selected_mode, {}).get(logical_step)

    def _finish_plan_for_task(self, event: dict[str, Any]) -> None:
        if self.selected_mode == "diagnosis":
            self._set_logical_step("evaluate", "done")
        elif self._run_summary.get("apply") == "awaiting confirmation":
            self._set_logical_step("apply", "waiting")
        elif self._run_summary.get("verify") == "passed":
            self._set_logical_step("restore", "done")
        elif event.get("status") == "failed":
            self._set_logical_step("verify", "failed")

    def _redraw_plan_tree(self) -> None:
        root = self._phase_strip.root
        root.remove_children()
        for index, step in enumerate(self._plan_steps, start=1):
            state = self._plan_states[index - 1]
            root.add(
                f"{self._state_icon(state)} {index}. "
                f"{self._short_step_label(step)}"
            )
        self._phase_strip.root.expand()

    def _reset_run_summary(self) -> None:
        self._run_summary = {
            "task": "-",
            "command": "-",
            "error": "-",
            "memory": "-",
            "plan": "-",
            "review": "-",
            "apply": "-",
            "verify": "-",
            "final": "-",
        }
        self._render_summary()

    def _render_summary(self) -> None:
        self._summary.clear()
        lines = [
            "Run Summary",
            f"Task: {self._run_summary.get('task', '-')}",
            f"Command: {self._run_summary.get('command', '-')}",
            f"Error: {self._run_summary.get('error', '-')}",
            f"Memory: {self._run_summary.get('memory', '-')}",
            f"Plan: {self._run_summary.get('plan', '-')}",
            f"Review: {self._run_summary.get('review', '-')}",
            f"Apply: {self._run_summary.get('apply', '-')}",
            f"Verify: {self._run_summary.get('verify', '-')}",
            f"Final: {self._run_summary.get('final', '-')}",
            f"Transcript: {self._transcript_name()}",
        ]
        self._summary.write(self._wrap_block("\n".join(lines), width=68))

    def _state_icon(self, state: str) -> str:
        return {
            "idle": "[ ]",
            "active": "[>]",
            "waiting": "[?]",
            "done": "[x]",
            "failed": "[!]",
            "skipped": "[-]",
        }.get(state, "[ ]")

    def _timeline_line(self, event: dict[str, Any]) -> str:
        timestamp = str(event.get("timestamp", ""))[11:19]
        event_type = event.get("type", "UnknownEvent")
        task_id = event.get("task_id", "-")
        return f"{timestamp} #{self._event_count:02d} {event_type} ({task_id})"

    def _format_list(self, items: list[Any]) -> str:
        if not items:
            return "- none"
        return "\n".join(
            self._wrap_block(f"- {item}", width=68, subsequent_indent="  ")
            for item in items
        )

    def _transcript_name(self) -> str:
        if self._transcript_path is None:
            return "-"
        return self._transcript_path.name

    def _format_diff(self, diff: str) -> str:
        if not diff:
            return "(no diff)"
        formatted: list[str] = []
        for line in diff.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                formatted.append(f"ADD {line}")
            elif line.startswith("-") and not line.startswith("---"):
                formatted.append(f"DEL {line}")
            else:
                formatted.append(f"    {line}")
        return "\n".join(formatted)

    def _card(self, title: str, lines: list[str]) -> str:
        body = "\n".join(lines)
        return self._wrap_block(f"\n=== {title} ===\n{body}\n", width=68)

    def _wrap_block(
        self,
        text: str,
        width: int,
        subsequent_indent: str = "",
    ) -> str:
        wrapped_lines: list[str] = []
        for line in str(text).splitlines():
            if not line:
                wrapped_lines.append("")
                continue
            wrapped_lines.extend(
                textwrap.wrap(
                    line,
                    width=width,
                    break_long_words=True,
                    break_on_hyphens=False,
                    subsequent_indent=subsequent_indent,
                )
                or [line]
            )
        return "\n".join(wrapped_lines)

    def _short_step_label(self, step: str) -> str:
        replacements = {
            "Load benchmark task metadata": "Load metadata",
            "Run the task entry command": "Run command",
            "Run the original benchmark command": "Run original",
            "Parse the runtime failure": "Parse failure",
            "Parse runtime failure": "Parse failure",
            "Generate structured failure memory": "Build memory",
            "Evaluate diagnosis against expected benchmark criteria": (
                "Evaluate diagnosis"
            ),
            "Generate patch plan": "Generate patch",
            "Apply patch plan": "Apply patch",
            "Run verification command": "Verify",
            "Restore original benchmark file": "Restore original",
        }
        if step in replacements:
            return replacements[step]
        return self._wrap_block(step, width=24).splitlines()[0]

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
    def _timeline(self) -> RichLog:
        return self.query_one("#timeline-panel", RichLog)

    @property
    def _summary(self) -> RichLog:
        return self.query_one("#summary-panel", RichLog)

    @property
    def _diagnosis(self) -> RichLog:
        return self.query_one("#diagnosis-panel", RichLog)

    @property
    def _repair(self) -> RichLog:
        return self.query_one("#repair-panel", RichLog)

    @property
    def _task_details(self) -> Static:
        return self.query_one("#task-details", Static)

    @property
    def _phase_strip(self) -> Tree:
        return self.query_one("#phase-strip", Tree)
