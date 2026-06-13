import sys
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
TestClient = pytest.importorskip("fastapi.testclient").TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.frontend.web_demo.server import app


def test_web_homepage_returns_html() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "SciCodePilot" in response.text


def test_tasks_api_returns_tasks() -> None:
    client = TestClient(app)

    response = client.get("/api/tasks")

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert data["tasks"]
    assert "task_id" in data["tasks"][0]


def test_unknown_task_stream_returns_404() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/run/stream?task_id=unknown_task&mode=diagnosis&confirm_apply=false"
    )

    assert response.status_code == 404
