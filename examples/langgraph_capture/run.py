"""LangGraph capture example — automatic callbacks, no RunRecorder hooks.

Run:
    uv sync --group langgraph
    uv run python examples/langgraph_capture/run.py
    uv run varly verify examples/langgraph_capture/artifacts/run.json \\
        --contract examples/policies/mvp.yaml --source langgraph
"""

from __future__ import annotations

import argparse
import uuid
from pathlib import Path
from typing import TypedDict

from langchain_core.language_models.fake import FakeListLLM
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

from varly.capture.langgraph_callbacks import LangGraphCallbackCollector

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "artifacts" / "run.json"


class AgentState(TypedDict):
    query: str
    answer: str


@tool
def search(query: str) -> str:
    """Search for factual information."""
    return "Paris is the capital of France."


def plan_with_llm(state: AgentState) -> AgentState:
    llm = FakeListLLM(responses=[f"Search for: {state['query']}"])
    llm.invoke(state["query"])
    return state


def run_search_tool(state: AgentState) -> AgentState:
    answer = search.invoke(state["query"])
    return {**state, "answer": answer}


def answer_with_llm(state: AgentState) -> AgentState:
    llm = FakeListLLM(responses=[state["answer"]])
    llm.invoke(state["answer"])
    return state


def build_graph() -> StateGraph:
    builder: StateGraph = StateGraph(AgentState)
    builder.add_node("plan", plan_with_llm)
    builder.add_node("search", run_search_tool)
    builder.add_node("answer", answer_with_llm)
    builder.add_edge(START, "plan")
    builder.add_edge("plan", "search")
    builder.add_edge("search", "answer")
    builder.add_edge("answer", END)
    return builder.compile()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a mock LangGraph agent and export callback events.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Where to write the callback export JSON",
    )
    return parser


def run(output: Path) -> Path:
    run_id = f"langgraph-capture-{uuid.uuid4().hex[:8]}"
    collector = LangGraphCallbackCollector(run_id=run_id)
    graph = build_graph()
    graph.invoke(
        {"query": "capital of France", "answer": ""},
        config={"callbacks": [collector]},
    )
    return collector.write_json(output)


def main() -> None:
    args = build_parser().parse_args()
    output = run(args.output)
    print(f"LangGraph capture written: {output}")
    print("Verify with:")
    print(
        f"  uv run varly verify {output} "
        "--contract examples/policies/mvp.yaml --source langgraph"
    )


if __name__ == "__main__":
    main()
