"""Optional local helper for live SDK recording.

CI never sets varly_LIVE. This stub does not call paid APIs.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

RECORDED_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "recorded"


def main() -> int:
    live = os.environ.get("varly_LIVE") == "1"
    if not live:
        print(
            "Live recording is disabled. Set varly_LIVE=1 and "
            "OPENAI_API_KEY (or a LangGraph export) on your machine.",
            file=sys.stderr,
        )
        print(
            "This script never runs in CI and does not send network requests.",
            file=sys.stderr,
        )
        return 2

    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "varly_LIVE=1 requires OPENAI_API_KEY in the environment.",
            file=sys.stderr,
        )
        return 1

    print("Live mode enabled. This stub does not call OpenAI or LangGraph.")
    print(f"Save an anonymized JSON export under: {RECORDED_DIR}")
    print("Then verify with --source openai or --source langgraph.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
