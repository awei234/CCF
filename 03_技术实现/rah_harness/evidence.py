from __future__ import annotations


_REQUIRED = ("run_id", "task_id", "assembly", "model", "terminal_status", "trace_path",
             "token_usage", "latency_seconds", "api_cost_usd")


def validate_run_record(record: dict[str, object]) -> list[str]:
    return [f"missing {field}" for field in _REQUIRED if field not in record]

