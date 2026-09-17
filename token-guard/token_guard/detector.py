from __future__ import annotations
from .config import GuardConfig
from .models import RequestRecord, Violation
from .storage import Storage

class WasteDetector:
    def __init__(self, storage: Storage, config: GuardConfig): self.storage, self.config = storage, config
    def check(self, record: RequestRecord) -> list[Violation]:
        issues: list[Violation] = []
        if record.fingerprint:
            repeats = len(self.storage.recent_matching(record.fingerprint, record.task_id, self.config.duplicate_window)) + 1
            if repeats >= self.config.duplicate_threshold:
                issues.append(Violation("duplicate_request", 3, f"Similar request seen {repeats} times (threshold: {self.config.duplicate_threshold}).", record.total_tokens, record.cost_usd))
        if record.input_tokens > self.config.max_context_tokens:
            issues.append(Violation("oversized_context", 2, f"Input context is {record.input_tokens:,} tokens.", record.input_tokens - self.config.max_context_tokens, 0))
        if record.output_tokens > self.config.max_output_tokens:
            issues.append(Violation("excessive_output", 2, f"Output is {record.output_tokens:,} tokens.", record.output_tokens - self.config.max_output_tokens, 0))
        recent = self.storage.timeline(20)
        costs = [float(x["cost_usd"]) for x in recent if x["cost_usd"] > 0]
        if len(costs) >= 5 and record.cost_usd > (sum(costs) / len(costs)) * self.config.cost_anomaly_multiplier:
            issues.append(Violation("cost_anomaly", 2, "Request cost is unusually high compared with recent traffic.", 0, record.cost_usd))
        return issues
