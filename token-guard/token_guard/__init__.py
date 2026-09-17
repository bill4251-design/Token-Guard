"""Token Guard: local-first token usage telemetry and waste detection."""
from .guard import TokenGuard, ViolationBlocked

__version__ = "0.1.0"
__all__ = ["TokenGuard", "ViolationBlocked"]
