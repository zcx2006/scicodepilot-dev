import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.events.bus import EventBus
from scicodepilot.events.schema import (
    CommandFinished,
    CommandOutput,
    CommandStarted,
)
from scicodepilot.tools.command_result import CommandResult
from scicodepilot.tools.shell_tool import ShellTool


@pytest.mark.asyncio
async def test_shell_tool_returns_command_result_and_emits_events() -> None:
    event_bus = EventBus()
    shell_tool = ShellTool(event_bus)

    command = f"{sys.executable} -c \"print('hello-shell-tool')\""
    result = await shell_tool.run(task_id="test_task", command=command)

    assert isinstance(result, CommandResult)
    assert result.return_code == 0
    assert result.success is True
    assert "hello-shell-tool" in result.stdout_lines
    assert result.stderr_lines == []

    events = []
    for _ in range(event_bus.queue_size):
        events.append(await event_bus.next_event())

    event_types = {event.type for event in events}
    assert "CommandStarted" in event_types
    assert "CommandOutput" in event_types
    assert "CommandFinished" in event_types

    assert any(isinstance(event, CommandStarted) for event in events)
    assert any(
        isinstance(event, CommandOutput) and event.content == "hello-shell-tool"
        for event in events
    )
    assert any(
        isinstance(event, CommandFinished)
        and event.return_code == 0
        and event.success is True
        for event in events
    )
