from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    required_args: tuple[str, ...]
    estimated_cost: float
    reversible: bool
    permission: str


@dataclass(frozen=True)
class ExpectedSignature:
    required_fields: tuple[str, ...] = ()


@dataclass
class ExecutionEvent:
    task_id: str
    run_id: str
    tool: str
    route_score: float | None = None
    blocked: bool = False
    rolled_back: bool = False
    repaired_depth: int | None = None
    failure_reason: str | None = None
    output_valid: bool | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_tool_call(tool: ToolSpec, arguments: dict[str, Any], expected: ExpectedSignature,
                       task_id: str = "", run_id: str = "") -> ExecutionEvent:
    missing = [name for name in tool.required_args if name not in arguments]
    if missing:
        return ExecutionEvent(
            task_id=task_id,
            run_id=run_id,
            tool=tool.name,
            blocked=True,
            failure_reason=f"missing required arguments: {', '.join(missing)}",
        )
    return ExecutionEvent(task_id=task_id, run_id=run_id, tool=tool.name)


def validate_output(event: ExecutionEvent, output: dict[str, Any], expected: ExpectedSignature) -> ExecutionEvent:
    missing = [name for name in expected.required_fields if name not in output]
    event.output_valid = not missing
    if missing:
        event.failure_reason = f"missing expected output fields: {', '.join(missing)}"
    return event

