from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json

# Keep configuration alongside the local database by default. This avoids a
# hidden user-home write and makes a project portable as a directory.
DEFAULT_CONFIG_PATH = Path(".token-guard.json")

@dataclass
class GuardConfig:
    strictness: int = 5
    action: str = "warn"  # warn | block
    duplicate_window: int = 60
    max_context_tokens: int = 32_000
    max_output_tokens: int = 8_000
    cost_anomaly_multiplier: float = 3.0

    def validate(self) -> None:
        if not 1 <= self.strictness <= 10:
            raise ValueError("strictness must be from 1 to 10")
        if self.action not in {"warn", "block"}:
            raise ValueError("action must be 'warn' or 'block'")

    @property
    def duplicate_threshold(self) -> int:
        # 1 (relaxed) => 9; 10 (strict) => 4, rounded dynamic interpolation.
        return round(9 - (self.strictness - 1) * 5 / 9)

    def to_dict(self) -> dict:
        return {**asdict(self), "duplicate_threshold": self.duplicate_threshold}

def load_config(path: str | Path | None = None) -> GuardConfig:
    file = Path(path) if path else DEFAULT_CONFIG_PATH
    if not file.exists(): return GuardConfig()
    config = GuardConfig(**json.loads(file.read_text(encoding="utf-8")))
    config.validate()
    return config

def save_config(config: GuardConfig, path: str | Path | None = None) -> None:
    config.validate()
    file = Path(path) if path else DEFAULT_CONFIG_PATH
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
