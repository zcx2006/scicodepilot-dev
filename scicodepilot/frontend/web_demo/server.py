from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict

STATIC_DIR = Path(__file__).resolve().parent / "static"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_LOG_DIR = PROJECT_ROOT / "outputs" / "frontend_logs"
REPORT_ASSETS_DIR = PROJECT_ROOT / "report_assets"


def _task_to_dict(task: Any) -> dict[str, Any]:
    if hasattr(task, "model_dump"):
        return task.model_dump(mode="json")
    if hasattr(task, "dict"):
        return task.dict()
    return dict(task)


def _sse_payload(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _format_transcript_event(event: dict[str, Any]) -> str:
    timestamp = str(event.get("timestamp", ""))
    clock = timestamp[11:19] if len(timestamp) >= 19 else "--:--:--"
    event_type = event.get("type", "UnknownEvent")
    task_id = event.get("task_id", "-")

    if event_type == "CommandStarted":
        return f"{clock} {event_type} ({task_id}) command={event.get('command')}"
    if event_type == "CommandOutput":
        return (
            f"{clock} {event_type} ({task_id}) "
            f"{event.get('stream')}: {event.get('content')}"
        )
    if event_type == "ErrorDetected":
        return (
            f"{clock} {event_type} ({task_id}) "
            f"{event.get('error_type')}: {event.get('summary')}"
        )
    if event_type == "PatchProposed":
        return (
            f"{clock} {event_type} ({task_id}) "
            f"target={event.get('target_file')} confidence={event.get('confidence')}"
        )
    if event_type == "PatchReviewCreated":
        return (
            f"{clock} {event_type} ({task_id}) "
            f"approved={event.get('approved')} blocked={event.get('blocked')} "
            f"risk={event.get('risk_level')}"
        )
    if event_type == "VerificationFinished":
        return (
            f"{clock} {event_type} ({task_id}) "
            f"success={event.get('success')} return_code={event.get('return_code')}"
        )
    if event_type == "TaskFinished":
        return (
            f"{clock} {event_type} ({task_id}) "
            f"status={event.get('status')} summary={event.get('summary')}"
        )
    return f"{clock} {event_type} ({task_id})"


def create_app(controller: BackendController | None = None) -> FastAPI:
    app = FastAPI(
        title="SciCodePilot Web Demo",
        description="Web demo for structured scientific-code diagnosis and repair.",
    )
    app.state.controller = controller or BackendController()

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    if REPORT_ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=REPORT_ASSETS_DIR), name="assets")

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/tasks")
    async def list_tasks() -> dict[str, list[dict[str, Any]]]:
        tasks = [_task_to_dict(task) for task in app.state.controller.list_tasks()]
        return {"tasks": tasks}

    @app.get("/api/run/stream")
    async def run_stream(
        task_id: str = Query(..., min_length=1),
        mode: str = Query("diagnosis", pattern="^(diagnosis|repair)$"),
        confirm_apply: bool = Query(False),
    ) -> StreamingResponse:
        try:
            app.state.controller.get_task(task_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        async def event_generator():
            FRONTEND_LOG_DIR.mkdir(parents=True, exist_ok=True)
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            transcript_path = (
                FRONTEND_LOG_DIR
                / f"{run_id}_{task_id}_{mode}_web_transcript.jsonl"
            )
            readable_path = (
                FRONTEND_LOG_DIR
                / f"{run_id}_{task_id}_{mode}_web_transcript.md"
            )
            header = (
                "# SciCodePilot Web Demo Transcript\n\n"
                f"- Task: `{task_id}`\n"
                f"- Mode: `{mode}`\n"
                f"- Confirm apply: `{confirm_apply}`\n\n"
            )
            readable_path.write_text(header, encoding="utf-8")

            meta_event = {
                "type": "TranscriptCreated",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "path": str(readable_path),
                "jsonl_path": str(transcript_path),
            }
            yield _sse_payload(meta_event)

            try:
                async for event in app.state.controller.run_task(
                    task_id=task_id,
                    mode=mode,
                    confirm_apply=confirm_apply,
                ):
                    event_dict = event_to_dict(event)
                    with transcript_path.open("a", encoding="utf-8") as stream:
                        stream.write(json.dumps(event_dict, ensure_ascii=False) + "\n")
                    with readable_path.open("a", encoding="utf-8") as stream:
                        stream.write(f"- {_format_transcript_event(event_dict)}\n")
                    yield _sse_payload(event_dict)
            except Exception as exc:
                error_event = {
                    "type": "FrontendStreamError",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                    "message": str(exc),
                }
                yield _sse_payload(error_event)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app


app = create_app()
