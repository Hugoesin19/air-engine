"""External-format adapters that translate telemetry into AIR traces."""

from air_engine.adapters.errors import (
    AdapterError,
    AdapterValidationError,
    UnsupportedFormatError,
)
from air_engine.adapters.json.adapter import adapt_file as adapt_json_file
from air_engine.adapters.json.adapter import adapt_payload as adapt_json_payload
from air_engine.adapters.langgraph.adapter import adapt_file as adapt_langgraph_file
from air_engine.adapters.langgraph.adapter import (
    adapt_payload as adapt_langgraph_payload,
)
from air_engine.adapters.openai.adapter import adapt_file as adapt_openai_file
from air_engine.adapters.openai.adapter import adapt_payload as adapt_openai_payload

__all__ = [
    "AdapterError",
    "AdapterValidationError",
    "UnsupportedFormatError",
    "adapt_json_file",
    "adapt_json_payload",
    "adapt_langgraph_file",
    "adapt_langgraph_payload",
    "adapt_openai_file",
    "adapt_openai_payload",
]
