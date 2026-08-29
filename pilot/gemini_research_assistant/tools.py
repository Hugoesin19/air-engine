"""Deterministic tools for the pilot research assistant."""

from __future__ import annotations

# Fixed corpus — no network, no extra API calls.
_SEARCH_RESULTS: dict[str, str] = {
    "capital of france": "Paris is the capital and largest city of France.",
    "air-engine": (
        "air-engine is a deterministic post-mortem verification engine "
        "for AI agent runs using AIR causal graphs and YAML contracts."
    ),
}


def search(query: str) -> str:
    """Return a canned snippet for a normalized query."""
    key = query.strip().lower()
    for needle, snippet in _SEARCH_RESULTS.items():
        if needle in key or key in needle:
            return snippet
    return (
        f"No canned result for query: {query!r}. "
        "Try 'capital of France' or 'air-engine'."
    )
