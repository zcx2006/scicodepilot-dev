import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict


def print_task_list(controller: BackendController) -> None:
    print("=== Available Tasks ===")
    for task in controller.list_tasks():
        requires = ", ".join(task.requires) if task.requires else "none"
        print(f"- {task.task_id}: {task.task_name} (requires: {requires})")


def print_frontend_event(event_dict: dict) -> None:
    event_type = event_dict["type"]

    if event_type == "TaskStarted":
        print(f"[TaskStarted] {event_dict['task_id']} - {event_dict['task_name']}")
    elif event_type == "CommandOutput":
        print(f"[CommandOutput:{event_dict['stream']}] {event_dict['content']}")
    elif event_type == "ErrorDetected":
        print(f"[ErrorDetected] {event_dict['error_type']} - {event_dict['summary']}")
    elif event_type == "PatchProposed":
        print(
            f"[PatchProposed] target_file={event_dict['target_file']} "
            f"confidence={event_dict['confidence']}"
        )
    elif event_type == "PatchApprovalRequired":
        print(
            f"[PatchApprovalRequired] target_file={event_dict['target_file']} - "
            f"{event_dict['message']}"
        )
    elif event_type == "PatchApplied":
        print(
            f"[PatchApplied] success={event_dict['success']} "
            f"target_file={event_dict['target_file']}"
        )
    elif event_type == "VerificationFinished":
        print(
            f"[VerificationFinished] success={event_dict['success']} "
            f"return_code={event_dict['return_code']}"
        )
    elif event_type == "FailureMemoryCreated":
        print(f"[FailureMemoryCreated] {event_dict['error_type']}")
    elif event_type == "TaskFinished":
        print(f"[TaskFinished] {event_dict['status']} - {event_dict['summary']}")
    else:
        print(f"[{event_type}]")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", default="repair_tensor_shape_001")
    parser.add_argument(
        "--mode",
        choices=["diagnosis", "repair"],
        default="repair",
    )
    parser.add_argument("--confirm-apply", action="store_true")
    args = parser.parse_args()

    controller = BackendController()
    print_task_list(controller)
    print()
    print(
        "=== Running Task ===\n"
        f"task_id: {args.task_id}\n"
        f"mode: {args.mode}\n"
        f"confirm_apply: {args.confirm_apply}"
    )

    async for event in controller.run_task(
        task_id=args.task_id,
        mode=args.mode,
        confirm_apply=args.confirm_apply,
    ):
        print_frontend_event(event_to_dict(event))


if __name__ == "__main__":
    asyncio.run(main())
