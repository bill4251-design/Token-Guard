from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Literal

Action = Literal["warn", "block"]

@dataclass
class RequestRecord:
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    latency_ms: float = 0
    cost_usd: float = 0
    task_id: str | None = None
    request_id: str | None = None
    fingerprint: str | None = None
    created_at: str | None = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens + self.cached_tokens

    def values(self) -> dict:
        result = asdict(self)
        result["total_tokens"] = self.total_tokens
        result["created_at"] = self.created_at or datetime.now(timezone.utc).isoformat()
        return result

@dataclass
class Violation:
    rule: str
    severity: int
    message: str
    estimated_waste_tokens: int = 0
    estimated_waste_usd: float = 0
