import json
from datetime import datetime

from scicodepilot.events.schema import Event


def event_to_dict(event: Event) -> dict:
    """Convert any backend event model into a frontend-friendly dict."""
    if hasattr(event, "model_dump"):
        return event.model_dump(mode="json")

    data = event.dict()
    timestamp = data.get("timestamp")
    if isinstance(timestamp, datetime):
        data["timestamp"] = timestamp.isoformat()
    return data


def event_to_json(event: Event) -> str:
    """Convert any backend event model into a JSON string."""
    return json.dumps(event_to_dict(event), ensure_ascii=False)
