from token_guard import TokenGuard
from token_guard.models import RequestRecord

guard = TokenGuard("example.db")
warnings = guard.record(RequestRecord(provider="openai", model="gpt-4.1-mini", input_tokens=120, output_tokens=80, cost_usd=0.0001, task_id="demo"), content="Write a Python hello world example")
print([warning.message for warning in warnings])
