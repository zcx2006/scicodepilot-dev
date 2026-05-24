import asyncio

from scicodepilot.events.schema import Event


class EventBus:
    """A minimal in-process async event bus backed by asyncio.Queue."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Event] = asyncio.Queue()

    async def emit(self, event: Event) -> None:
        """Publish one event into the queue."""
        await self._queue.put(event)

    async def next_event(self) -> Event:
        """Wait for and return the next event from the queue."""
        return await self._queue.get()

    @property
    def queue_size(self) -> int:
        """Return the current number of queued events for simple debugging."""
        return self._queue.qsize()
