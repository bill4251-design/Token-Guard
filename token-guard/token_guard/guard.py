from __future__ import annotations
import hashlib
from pathlib import Path
from .config import GuardConfig, load_config
from .detector import WasteDetector
from .models import RequestRecord, Violation
from .storage import Storage

class ViolationBlocked(RuntimeError):
    pass

class TokenGuard:
    def __init__(self, db_path: str | Path = "token-guard.db", config: GuardConfig | None = None):
        self.config = config or load_config()
        self.storage = Storage(db_path)
        self.detector = WasteDetector(self.storage, self.config)

    @staticmethod
    def fingerprint(content: str) -> str:
        """One-way local hash; raw prompt/code is never persisted."""
        normalized = " ".join(content.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()

    def record(self, record: RequestRecord, content: str | None = None) -> list[Violation]:
        if content and not record.fingerprint: record.fingerprint = self.fingerprint(content)
        violations = self.detector.check(record)
        values = record.values(); record.created_at = values["created_at"]
        self.storage.add_request(record)
        for issue in violations: self.storage.add_violation(record.request_id, issue, record.created_at)
        if violations and self.config.action == "block":
            raise ViolationBlocked(violations[0].message)
        return violations

    def close(self) -> None:
        """Release the local SQLite file explicitly (important on Windows)."""
        self.storage.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
