"""Collect LangChain/LangGraph callbacks into varly's export format.

Requires the optional ``langgraph`` dependency group or
``pip install varly[langgraph]``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

CALLBACK_OBJECT = "langgraph.callback_events"


def _parent_ids(parent_run_id: UUID | None) -> list[str]:
    if parent_run_id is None:
        return []
    return [str(parent_run_id)]


def _serialize(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return repr(value)


def _name_from_serialized(serialized: dict[str, Any] | None, fallback: str) -> str:
    if isinstance(serialized, dict):
        name = serialized.get("name")
        if isinstance(name, str) and name:
            return name
        id_path = serialized.get("id")
        if isinstance(id_path, list) and id_path:
            tail = id_path[-1]
            if isinstance(tail, str) and tail:
                return tail
    return fallback


def _llm_output_data(response: Any) -> dict[str, Any]:
    llm_output: dict[str, Any] = {}
    generations: list[list[dict[str, str]]] = []
    if hasattr(response, "generations"):
        for generation_row in response.generations:
            row: list[dict[str, str]] = []
            for generation in generation_row:
                text = getattr(generation, "text", None)
                if isinstance(text, str):
                    row.append({"text": text})
            if row:
                generations.append(row)
    if generations:
        llm_output["generations"] = generations

    usage = getattr(response, "llm_output", None)
    if isinstance(usage, dict) and usage.get("token_usage"):
        llm_output["token_usage"] = _serialize(usage["token_usage"])
    elif hasattr(response, "response_metadata"):
        metadata = response.response_metadata
        if isinstance(metadata, dict):
            token_usage = metadata.get("token_usage")
            if isinstance(token_usage, dict):
                llm_output["token_usage"] = _serialize(token_usage)

    if not llm_output and response is not None:
        return {"output": _serialize(response)}
    return {"output": {"llm_output": llm_output, "generations": generations or None}}


def _build_collector_class() -> type:
    try:
        from langchain_core.callbacks import BaseCallbackHandler
    except ImportError as exc:
        msg = (
            "LangGraph capture requires langchain-core. "
            "Install with: pip install 'varly[langgraph]' or uv sync --group langgraph"
        )
        raise ImportError(msg) from exc

    class LangGraphCallbackCollector(BaseCallbackHandler):
        """Record LangChain/LangGraph callbacks for ``verify --source langgraph``."""

        def __init__(self, *, run_id: str | None = None) -> None:
            super().__init__()
            self._explicit_run_id = run_id
            self._root_run_id: str | None = run_id
            self._events: list[dict[str, Any]] = []
            self._run_names: dict[str, str] = {}

        def _remember_name(self, run_id: UUID, name: str) -> None:
            self._run_names[str(run_id)] = name

        def _lookup_name(self, run_id: UUID, fallback: str) -> str:
            return self._run_names.get(str(run_id), fallback)

        @property
        def events(self) -> list[dict[str, Any]]:
            return list(self._events)

        def _append(
            self,
            event: str,
            *,
            name: str,
            run_id: UUID,
            parent_run_id: UUID | None,
            data: dict[str, Any] | None = None,
        ) -> None:
            self._events.append(
                {
                    "event": event,
                    "name": name,
                    "run_id": str(run_id),
                    "parent_ids": _parent_ids(parent_run_id),
                    "data": _serialize(data or {}),
                }
            )
            if (
                event == "on_chain_start"
                and parent_run_id is None
                and self._root_run_id is None
            ):
                self._root_run_id = str(run_id)

        def on_chain_start(
            self,
            serialized: dict[str, Any],
            inputs: dict[str, Any],
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            self._append(
                "on_chain_start",
                name=_name_from_serialized(serialized, "LangGraph"),
                run_id=run_id,
                parent_run_id=parent_run_id,
                data={"input": inputs},
            )

        def on_chain_end(
            self,
            outputs: dict[str, Any],
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            self._append(
                "on_chain_end",
                name="LangGraph",
                run_id=run_id,
                parent_run_id=parent_run_id,
                data={"output": outputs},
            )

        def on_chat_model_start(
            self,
            serialized: dict[str, Any],
            messages: list[list[Any]],
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            name = _name_from_serialized(serialized, "ChatModel")
            self._remember_name(run_id, name)
            self._append(
                "on_chat_model_start",
                name=name,
                run_id=run_id,
                parent_run_id=parent_run_id,
                data={},
            )

        def on_chat_model_end(
            self,
            response: Any,
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            self._append(
                "on_chat_model_end",
                name=self._lookup_name(run_id, "ChatModel"),
                run_id=run_id,
                parent_run_id=parent_run_id,
                data=_llm_output_data(response),
            )

        def on_llm_start(
            self,
            serialized: dict[str, Any],
            prompts: list[str],
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            name = _name_from_serialized(serialized, "LLM")
            self._remember_name(run_id, name)
            self._append(
                "on_llm_start",
                name=name,
                run_id=run_id,
                parent_run_id=parent_run_id,
                data={},
            )

        def on_llm_end(
            self,
            response: Any,
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            self._append(
                "on_llm_end",
                name=self._lookup_name(run_id, "LLM"),
                run_id=run_id,
                parent_run_id=parent_run_id,
                data=_llm_output_data(response),
            )

        def on_tool_start(
            self,
            serialized: dict[str, Any],
            input_str: str,
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            name = _name_from_serialized(serialized, "tool")
            self._remember_name(run_id, name)
            self._append(
                "on_tool_start",
                name=name,
                run_id=run_id,
                parent_run_id=parent_run_id,
                data={"input": input_str},
            )

        def on_tool_end(
            self,
            output: Any,
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
        ) -> None:
            serialized = kwargs.get("serialized")
            fallback = _name_from_serialized(
                serialized if isinstance(serialized, dict) else None,
                "tool",
            )
            self._append(
                "on_tool_end",
                name=self._lookup_name(run_id, fallback),
                run_id=run_id,
                parent_run_id=parent_run_id,
                data={"output": output},
            )

        def to_payload(self) -> dict[str, Any]:
            run_id = (
                self._explicit_run_id or self._root_run_id or "langgraph-run-unknown"
            )
            return {
                "object": CALLBACK_OBJECT,
                "run_id": run_id,
                "events": self._events,
            }

        def write_json(self, path: Path) -> Path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(self.to_payload(), indent=2) + "\n",
                encoding="utf-8",
            )
            return path

    return LangGraphCallbackCollector


_CollectorClass: type | None = None


def LangGraphCallbackCollector(*, run_id: str | None = None) -> Any:
    """Create a callback collector compatible with LangChain/LangGraph runs."""
    global _CollectorClass  # noqa: PLW0603
    if _CollectorClass is None:
        _CollectorClass = _build_collector_class()
    return _CollectorClass(run_id=run_id)
