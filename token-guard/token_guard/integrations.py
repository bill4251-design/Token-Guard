"""Provider-normalising helpers. They keep API clients and response payloads outside storage."""
from __future__ import annotations
from typing import Any
from .models import RequestRecord

def from_openai(response: Any, model: str, **metadata: Any) -> RequestRecord:
    usage = getattr(response, "usage", None) or response.get("usage", {})
    get = lambda key: getattr(usage, key, None) if not isinstance(usage, dict) else usage.get(key)
    details = get("prompt_tokens_details") or {}
    cached = getattr(details, "cached_tokens", 0) if not isinstance(details, dict) else details.get("cached_tokens", 0)
    return RequestRecord(provider="openai", model=model, input_tokens=get("prompt_tokens") or get("input_tokens") or 0, output_tokens=get("completion_tokens") or get("output_tokens") or 0, cached_tokens=cached or 0, **metadata)

def from_anthropic(response: Any, model: str, **metadata: Any) -> RequestRecord:
    usage = getattr(response, "usage", None) or response.get("usage", {})
    get = lambda key: getattr(usage, key, None) if not isinstance(usage, dict) else usage.get(key)
    return RequestRecord(provider="anthropic", model=model, input_tokens=get("input_tokens") or 0, output_tokens=get("output_tokens") or 0, cached_tokens=get("cache_read_input_tokens") or 0, **metadata)

def from_compatible(response: Any, provider: str, model: str, **metadata: Any) -> RequestRecord:
    record = from_openai(response, model, **metadata)
    record.provider = provider
    return record
