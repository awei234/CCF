"""OpenAI-compatible DeepSeek agent for the fixed SOP-Bench protocol."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from .core import ExpectedSignature, ExecutionEvent, ToolSpec, validate_tool_call

try:  # SOP-Bench is an execution-time dependency, not a unit-test dependency.
    from amazon_sop_bench.agents.base import AgentResult, BaseAgent
except ImportError:
    @dataclass
    class AgentResult:  # type: ignore[no-redef]
        output: Any
        tool_calls: list[dict[str, Any]]
        reasoning_trace: str | None = None
        execution_time: float = 0.0
        success: bool = True
        error: str | None = None

    class BaseAgent:  # type: ignore[no-redef]
        def __init__(self, model_id: str | None = None, **kwargs: Any) -> None:
            self.model_id = model_id


def create_deepseek_client(api_key: str, client_factory: Any | None = None) -> Any:
    """Construct a client without retaining or logging the credential."""
    if client_factory is None:
        from openai import OpenAI

        client_factory = OpenAI

    return client_factory(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        timeout=30,
        max_retries=0,
    )


class DeepSeekSopAgent(BaseAgent):
    """Capability-matched agent with auditable tool validation events."""

    def __init__(
        self,
        client: Any,
        assembly: str = "rah_full",
        model_id: str = "deepseek-v4-flash",
        max_steps: int = 20,
    ) -> None:
        super().__init__(model_id=model_id)
        self.client = client
        self.assembly = assembly
        self.max_steps = max_steps

    @staticmethod
    def _openai_tools(tool_manager: Any) -> tuple[list[dict[str, Any]], dict[str, ToolSpec]]:
        definitions: list[dict[str, Any]] = []
        safety_specs: dict[str, ToolSpec] = {}
        for raw_spec in tool_manager.get_tool_specs():
            spec = raw_spec.get("toolSpec", raw_spec)
            schema = spec.get("inputSchema", {}).get("json", {"type": "object"})
            name = spec["name"]
            definitions.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": spec.get("description", name),
                    "parameters": schema,
                },
            })
            safety_specs[name] = ToolSpec(
                name=name,
                description=spec.get("description", name),
                required_args=tuple(schema.get("required", [])),
                estimated_cost=0.0,
                reversible=True,
                permission="benchmark_mock",
            )
        return definitions, safety_specs

    def execute(self, sop: str, task: dict[str, Any], tools: Any) -> AgentResult:
        started = time.perf_counter()
        tool_definitions, safety_specs = self._openai_tools(tools)
        task_text = "\n".join(f"{key}: {value}" for key, value in task.items())
        messages: list[dict[str, Any]] = [{
            "role": "user",
            "content": (
                "Follow this SOP exactly and use tools where required. Return the final "
                "decision only as <final_decision>value</final_decision>.\n\n"
                f"SOP:\n{sop}\n\nTask:\n{task_text}"
            ),
        }]
        trace: list[dict[str, Any]] = []
        recorded_calls: list[dict[str, Any]] = []
        try:
            for step in range(1, self.max_steps + 1):
                completion = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    tools=tool_definitions,
                    temperature=0,
                )
                message = completion.choices[0].message
                tool_calls = list(message.tool_calls or [])
                trace.append({"phase": "model_response", "step": step, "tool_calls": len(tool_calls)})
                if not tool_calls:
                    return AgentResult(
                        output=message.content or "",
                        tool_calls=recorded_calls,
                        reasoning_trace=json.dumps(trace, ensure_ascii=False),
                        execution_time=time.perf_counter() - started,
                        success=True,
                        error=None,
                    )
                messages.append({"role": "assistant", "content": message.content or "", "tool_calls": tool_calls})
                for call in tool_calls:
                    arguments = json.loads(call.function.arguments or "{}")
                    name = call.function.name
                    event = validate_tool_call(
                        safety_specs[name], arguments, ExpectedSignature()
                    )
                    if event.blocked:
                        result_text = f"Blocked: {event.failure_reason}"
                        success = False
                        result = None
                    else:
                        executed = tools.execute_tool(name, arguments)
                        success = bool(executed.success)
                        result = executed.result if success else None
                        result_text = json.dumps(result if success else {"error": executed.error})
                    recorded_calls.append({
                        "tool": name, "input": arguments, "output": result,
                        "success": success, "step": step,
                    })
                    trace.append({
                        "phase": "tool_result", "step": step, "tool": name,
                        "blocked": event.blocked, "success": success,
                    })
                    messages.append({
                        "role": "tool", "tool_call_id": call.id, "content": result_text,
                    })
            return AgentResult(
                output="", tool_calls=recorded_calls,
                reasoning_trace=json.dumps(trace, ensure_ascii=False),
                execution_time=time.perf_counter() - started, success=False,
                error=f"max steps reached: {self.max_steps}",
            )
        except Exception as error:
            trace.append({"phase": "error", "error_type": type(error).__name__})
            return AgentResult(
                output="", tool_calls=recorded_calls,
                reasoning_trace=json.dumps(trace, ensure_ascii=False),
                execution_time=time.perf_counter() - started, success=False,
                error=f"provider {type(error).__name__}",
            )
