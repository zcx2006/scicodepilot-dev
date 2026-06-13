import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def smoke_test() -> None:
    from fastapi.testclient import TestClient

    from scicodepilot.frontend.web_demo.server import app

    client = TestClient(app)
    index_response = client.get("/")
    tasks_response = client.get("/api/tasks")

    assert index_response.status_code == 200
    assert tasks_response.status_code == 200
    assert "tasks" in tasks_response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    if args.smoke_test:
        smoke_test()
        print("Web demo smoke test passed.")
        return

    import uvicorn

    uvicorn.run(
        "scicodepilot.frontend.web_demo.server:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
