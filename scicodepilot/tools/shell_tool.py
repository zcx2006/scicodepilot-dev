import asyncio
from typing import Literal

from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import (
    CommandFinished,
    CommandOutput,
    CommandStarted,
)
from scicodepilot.tools.command_result import CommandResult


class ShellTool:
    """Run a shell command and stream stdout/stderr as backend events."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def run(
        self,
        task_id: str,
        command: str,
        cwd: str | None = None,
    ) -> CommandResult:
        """Execute command asynchronously and return its collected result.

        cwd lets benchmark tasks run their entry command inside the task repo.
        """
        await self.event_bus.emit(
            CommandStarted(task_id=task_id, command=command)
        )

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        async def read_stream(
            stream: asyncio.StreamReader | None,
            stream_name: Literal["stdout", "stderr"],
            collected_lines: list[str],
        ) -> None:
            """Read one output stream line by line and emit non-empty lines."""
            if stream is None:
                return

            while True:
                line = await stream.readline()
                if not line:
                    break

                content = line.decode("utf-8", errors="replace").strip()
                if not content:
                    continue

                collected_lines.append(content)
                await self.event_bus.emit(
                    CommandOutput(
                        task_id=task_id,
                        stream=stream_name,
                        content=content,
                    )
                )

        # Consume stdout and stderr concurrently so one stream cannot block the other.
        await asyncio.gather(
            read_stream(process.stdout, "stdout", stdout_lines),
            read_stream(process.stderr, "stderr", stderr_lines),
        )

        return_code = await process.wait()
        success = return_code == 0

        await self.event_bus.emit(
            CommandFinished(
                task_id=task_id,
                command=command,
                return_code=return_code,
                success=success,
            )
        )

        return CommandResult(
            command=command,
            return_code=return_code,
            success=success,
            stdout_lines=stdout_lines,
            stderr_lines=stderr_lines,
        )
