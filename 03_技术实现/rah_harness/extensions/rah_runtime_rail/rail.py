"""JiuwenSwarm extension entrypoint for recording RAH lifecycle traces."""

from __future__ import annotations

import json
from pathlib import Path

from openjiuwen.harness.rails import DeepAgentRail
from openjiuwen.core.single_agent.rail.base import AgentCallbackContext
from jiuwenswarm.common.utils import get_agent_workspace_dir


class RahRuntimeRail(DeepAgentRail):
    priority: int = 60

    def __init__(self, trace_path: str | None = None, assembly: str = "rah_full") -> None:
        self.trace_path = (
            Path(trace_path)
            if trace_path
            else get_agent_workspace_dir() / "rah_traces" / "web_lifecycle.jsonl"
        )
        self.assembly = assembly

    async def before_tool_call(self, ctx: AgentCallbackContext) -> None:
        self._record(ctx, "before_tool_call")

    async def after_tool_call(self, ctx: AgentCallbackContext) -> None:
        self._record(ctx, "after_tool_call")

    async def after_task_iteration(self, ctx: AgentCallbackContext) -> None:
        self._record(ctx, "after_task_iteration")

    def _record(self, ctx: AgentCallbackContext, phase: str) -> None:
        if self.trace_path is None:
            return
        session_id = str(getattr(ctx, "session_id", "unknown"))
        event = {"run_id": session_id, "task_id": session_id, "assembly": self.assembly,
                 "phase": phase}
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
