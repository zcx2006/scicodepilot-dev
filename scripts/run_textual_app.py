import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.frontend.textual_app import SciCodePilotTextualApp


async def smoke_test() -> None:
    app = SciCodePilotTextualApp()
    async with app.run_test() as pilot:
        await pilot.pause()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    if args.smoke_test:
        asyncio.run(smoke_test())
        return

    SciCodePilotTextualApp().run()


if __name__ == "__main__":
    main()
