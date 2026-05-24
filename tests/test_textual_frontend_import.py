import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_textual_app_imports_and_exposes_app_class() -> None:
    from scicodepilot.frontend.textual_app import SciCodePilotTextualApp

    assert SciCodePilotTextualApp is not None


def test_textual_app_entrypoint_exists() -> None:
    assert (PROJECT_ROOT / "scripts" / "run_textual_app.py").exists()
