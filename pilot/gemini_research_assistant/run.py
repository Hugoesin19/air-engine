"""Research assistant pilot with optional Gemini live mode and RunRecorder capture."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from air_engine.capture import RunRecorder

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from tools import search  # noqa: E402

PILOT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PILOT_DIR / "artifacts" / "research_run.json"
DEFAULT_QUESTION = "What is the capital of France?"
DEFAULT_RUN_ID = "pilot-research-20260829-0001"
DEFAULT_MODEL = "gemini-3.6-flash"


def _load_dotenv() -> None:
    """Load repo-root `.env` into the process (never committed; see .env.example)."""
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Gemini research-assistant pilot and write a capture log.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the capture JSON (default: pilot/artifacts/research_run.json)",
    )
    parser.add_argument(
        "--question",
        default=DEFAULT_QUESTION,
        help="User question for the assistant",
    )
    parser.add_argument(
        "--run-id",
        default=DEFAULT_RUN_ID,
        help="Stable run_id written into the capture log",
    )
    return parser


def _api_key() -> str | None:
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")


def _live_enabled() -> bool:
    return os.environ.get("PILOT_LIVE") == "1" and bool(_api_key())


def _extract_search_query(plan_text: str, *, fallback: str) -> str:
    match = re.search(r'"query"\s*:\s*"([^"]+)"', plan_text)
    if match:
        return match.group(1)
    lowered = plan_text.lower()
    if "france" in lowered or "paris" in lowered:
        return "capital of France"
    if "air-engine" in lowered or "air engine" in lowered:
        return "air-engine"
    return fallback


def _dry_plan(question: str) -> tuple[str, int]:
    query_value = "capital of France" if "france" in question.lower() else "air-engine"
    text = json.dumps(
        {
            "action": "search",
            "query": query_value,
            "reason": "dry-run planner",
        }
    )
    return text, 48


def _dry_answer(question: str, snippet: str) -> tuple[str, int]:
    text = f"Answer to {question!r}: {snippet}"
    return text, 62


def _call_gemini(*, prompt: str, model: str) -> tuple[str, int]:
    try:
        from google import genai
    except ImportError as exc:
        msg = "Live mode requires google-genai. Install with: uv sync --group pilot"
        raise RuntimeError(msg) from exc

    client = genai.Client(api_key=_api_key())
    response = client.models.generate_content(model=model, contents=prompt)
    text = (response.text or "").strip()
    usage = getattr(response, "usage_metadata", None)
    total = getattr(usage, "total_token_count", None) if usage else None
    if isinstance(total, int) and total > 0:
        tokens = int(total)
    else:
        tokens = max(len(text) // 4, 1)
    return text, tokens


def _plan(question: str, *, live: bool, model: str) -> tuple[str, int]:
    if not live:
        return _dry_plan(question)
    prompt = (
        "You are a research assistant planner. The user asked:\n"
        f"{question}\n\n"
        'Reply with ONLY a JSON object: {"action":"search","query":"<short query>"}. '
        "Use action search when external facts are needed."
    )
    return _call_gemini(prompt=prompt, model=model)


def _answer(question: str, snippet: str, *, live: bool, model: str) -> tuple[str, int]:
    if not live:
        return _dry_answer(question, snippet)
    prompt = (
        "Answer the user in one or two sentences using ONLY the snippet below.\n\n"
        f"Question: {question}\nSnippet: {snippet}"
    )
    return _call_gemini(prompt=prompt, model=model)


def run(
    *,
    output: Path,
    question: str,
    run_id: str,
    live: bool,
    model: str,
) -> Path:
    recorder = RunRecorder(run_id=run_id)
    started = time.perf_counter()

    def ts() -> float:
        return round((time.perf_counter() - started) * 1000, 3)

    recorder.record_run_start(step_id="pilot-step-010", timestamp_ms=ts())
    plan_text, plan_tokens = _plan(question, live=live, model=model)
    recorder.record_llm_call(
        step_id="pilot-step-011",
        timestamp_ms=ts(),
        total_tokens=plan_tokens,
    )

    query = _extract_search_query(plan_text, fallback=question)
    recorder.record_tool_call(
        step_id="pilot-step-012",
        timestamp_ms=ts(),
        name="search",
    )
    snippet = search(query)
    recorder.record_tool_output(
        step_id="pilot-step-013",
        timestamp_ms=ts(),
        name="search",
    )
    recorder.record_read(source="pilot-step-012", target="pilot-step-011")

    _, answer_tokens = _answer(question, snippet, live=live, model=model)
    recorder.record_llm_call(
        step_id="pilot-step-014",
        timestamp_ms=ts(),
        total_tokens=answer_tokens,
    )
    recorder.record_read(source="pilot-step-013", target="pilot-step-014")
    recorder.record_run_end(step_id="pilot-step-015", timestamp_ms=ts())

    return recorder.write_json(output)


def main() -> int:
    _load_dotenv()
    args = build_parser().parse_args()
    live = _live_enabled()
    model = os.environ.get("PILOT_GEMINI_MODEL", DEFAULT_MODEL)

    if os.environ.get("PILOT_LIVE") == "1" and not _api_key():
        print(
            "PILOT_LIVE=1 but no GOOGLE_API_KEY or GEMINI_API_KEY found. "
            "Falling back to dry-run.",
            file=sys.stderr,
        )

    mode = "live" if live else "dry-run"
    output = run(
        output=args.output,
        question=args.question,
        run_id=args.run_id,
        live=live,
        model=model,
    )
    print(f"Pilot capture written ({mode}): {output}")
    if not live:
        print(
            "Tip: PILOT_LIVE=1 and GOOGLE_API_KEY for a real Gemini capture.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
