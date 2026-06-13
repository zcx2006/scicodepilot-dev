import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_web_app_imports() -> None:
    pytest.importorskip("fastapi")

    from scicodepilot.frontend.web_demo.server import app

    assert app is not None


def test_web_demo_entrypoint_exists() -> None:
    assert (PROJECT_ROOT / "scripts" / "run_web_demo.py").exists()
