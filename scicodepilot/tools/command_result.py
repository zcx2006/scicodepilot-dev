from pydantic import BaseModel


class CommandResult(BaseModel):
    """Summary of one finished shell command.

    CommandOutput events are emitted line by line while the process is running.
    CommandResult is the completed, collected result returned after the process exits.
    """

    command: str
    return_code: int
    success: bool
    stdout_lines: list[str]
    stderr_lines: list[str]
