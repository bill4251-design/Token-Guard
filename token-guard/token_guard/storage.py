from __future__ import annotations
import sqlite3
from pathlib import Path
from .models import RequestRecord, Violation

class Storage:
    def __init__(self, path: str | Path = "token-guard.db"):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS requests (
          id INTEGER PRIMARY KEY, provider TEXT, model TEXT, input_tokens INTEGER,
          output_tokens INTEGER, cached_tokens INTEGER, total_tokens INTEGER, latency_ms REAL,
          cost_usd REAL, task_id TEXT, request_id TEXT, fingerprint TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS violations (
          id INTEGER PRIMARY KEY, request_id TEXT, rule TEXT, severity INTEGER, message TEXT,
          estimated_waste_tokens INTEGER, estimated_waste_usd REAL, created_at TEXT);
        """)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def add_request(self, record: RequestRecord) -> int:
        v = record.values()
        columns = ", ".join(v)
        cur = self.conn.execute(f"INSERT INTO requests ({columns}) VALUES ({', '.join('?' for _ in v)})", tuple(v.values()))
        self.conn.commit()
        return int(cur.lastrowid)

    def add_violation(self, request_id: str | None, violation: Violation, created_at: str) -> None:
        self.conn.execute("INSERT INTO violations (request_id,rule,severity,message,estimated_waste_tokens,estimated_waste_usd,created_at) VALUES (?,?,?,?,?,?,?)",
          (request_id, violation.rule, violation.severity, violation.message, violation.estimated_waste_tokens, violation.estimated_waste_usd, created_at))
        self.conn.commit()

    def recent_matching(self, fingerprint: str, task_id: str | None, seconds: int) -> list[sqlite3.Row]:
        scope = "task_id IS ?" if task_id is not None else "task_id IS NULL"
        return self.conn.execute(f"SELECT * FROM requests WHERE fingerprint=? AND {scope} AND created_at >= datetime('now', ?) ORDER BY id DESC", (fingerprint, task_id, f"-{seconds} seconds")).fetchall()

    def summary(self) -> dict:
        r = self.conn.execute("SELECT COUNT(*) requests, COALESCE(SUM(total_tokens),0) tokens, COALESCE(SUM(cost_usd),0) cost FROM requests").fetchone()
        v = self.conn.execute("SELECT COUNT(*) violations, COALESCE(SUM(estimated_waste_tokens),0) waste_tokens, COALESCE(SUM(estimated_waste_usd),0) waste_cost FROM violations").fetchone()
        return {**dict(r), **dict(v)}

    def timeline(self, limit: int = 100) -> list[dict]:
        return [dict(x) for x in self.conn.execute("SELECT * FROM requests ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

    def violations(self, limit: int = 100) -> list[dict]:
        return [dict(x) for x in self.conn.execute("SELECT * FROM violations ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
