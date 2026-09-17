# 🛡 Token Guard

**Local-first monitoring and guardrails for AI token waste.** Token Guard records request usage in SQLite, identifies waste patterns without storing prompts or code, and can warn—or stop your integration—when a rule is violated.

> Private by default: prompts, source code, and API keys never leave your machine and are not written to the database. Repetition detection uses a one-way local SHA-256 fingerprint.

## Quick start

```bash
git clone https://github.com/your-org/token-guard.git
cd token-guard
pip install -e .
python examples/basic.py
token-guard --db example.db report
token-guard --db example.db serve
```

Open `http://127.0.0.1:8787` for the dashboard. Run tests with `python -m unittest discover -s tests -v`.

## What it detects

| Rule | Detection | Estimated waste |
|---|---|---|
| Duplicate request / code | Same local fingerprint inside the task window | Current request |
| Retry loop | Repeated requests are surfaced by the duplicate rule | Current request |
| Oversized context | Input exceeds configured maximum | Excess input tokens |
| Excessive output | Output exceeds configured maximum | Excess output tokens |
| Cost anomaly | Cost greatly exceeds recent local baseline | Current request cost |

## Strictness and actions

`strictness` is a 1–10 slider. Level **1 (Relaxed)** permits 9 similar calls; level **10 (Strict)** permits 4. Values between them interpolate dynamically.

```bash
token-guard config --strictness 10 --action block
token-guard config --show
```

Actions are `warn` (the default: log and return violations) and `block` (log then raise `ViolationBlocked`; callers decide how to cancel work safely).

## SDK

```python
from token_guard import TokenGuard, ViolationBlocked
from token_guard.models import RequestRecord

guard = TokenGuard("token-guard.db")
try:
    alerts = guard.record(
        RequestRecord(provider="openai", model="gpt-4.1-mini", input_tokens=125,
                      output_tokens=42, cached_tokens=0, latency_ms=280, cost_usd=0.0003,
                      task_id="invoice-agent", request_id="req_123"),
        content="the request text or generated code")
except ViolationBlocked:
    # halt the surrounding agent operation
    pass
finally:
    guard.close()
```

`token_guard.integrations` provides `from_openai`, `from_anthropic`, and `from_compatible` helpers that turn common response usage objects into `RequestRecord`; your application still owns API calls and pricing calculation.

## Architecture

```text
Provider response → integration helper → TokenGuard.record()
                                          ├─ local SHA-256 fingerprint
                                          ├─ WasteDetector rules
                                          └─ SQLite → CLI / local dashboard
```

## CLI

```text
token-guard --db token-guard.db usage
token-guard --db token-guard.db report
token-guard config --strictness 6 --action warn
token-guard --db token-guard.db serve --port 8787
```

## Privacy, scope, and roadmap

This v0.1 MVP is intentionally dependency-light and runs entirely locally. It retains metadata, usage, cost, IDs, timestamps, and hashes—not raw content or credentials. Hashes can still signal equality, so protect the SQLite file under your normal local-data policy.

Next steps include configurable model-pricing tables, semantic similarity with an opt-in local model, richer retry classifications, framework middleware, and export controls. Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
