from __future__ import annotations

import random
from typing import Any

from rah_harness.core import ExecutionEvent, ExpectedSignature, ToolSpec, validate_output, validate_tool_call
from rah_harness.memory import BM25Memory
from rah_harness.planner import PlanTree
from rah_harness.router import route_tool


def _tools(count: int) -> list[ToolSpec]:
    return [ToolSpec(f"tool_{index}", f"perform tool_{index} workflow", (), 1.0 + index / 10, True, "read")
            for index in range(count)]


def run_synthetic(assembly: str, seed: int, depth: int, tool_count: int) -> dict[str, Any]:
    """Mechanism-only simulation: no method-specific accuracy or block probabilities."""
    if assembly not in {"react", "planner_only", "memory_only", "safety_only", "rah_full"}:
        raise ValueError(f"unknown assembly: {assembly}")
    rng = random.Random(seed)
    tools = _tools(tool_count)
    requirements = [f"tool_{rng.randrange(tool_count)}" for _ in range(depth)]
    plan = PlanTree.from_paths([tuple(["root", *[f"step_{index}" for index in range(depth)]])])
    memory = BM25Memory(capacity=10, top_k=2)
    events: list[dict[str, Any]] = []
    failures = 0
    for index, required in enumerate(requirements):
        task = f"perform {required} workflow"
        if assembly in {"planner_only", "memory_only", "safety_only", "rah_full"}:
            chosen = route_tool(task, tools).tool
        else:
            chosen = tools[rng.randrange(tool_count)]
        event = validate_tool_call(chosen, {}, ExpectedSignature(), f"synthetic-{seed}", f"{assembly}-{seed}")
        event.route_score = 1.0 if chosen.name == required else 0.0
        output = {"accepted": True} if chosen.name == required else {"error": "wrong tool"}
        validate_output(event, output, ExpectedSignature(required_fields=("accepted",)))
        if not event.output_valid:
            failures += 1
            memory.add(f"step {index} failed with {chosen.name}; expected {required}")
            if assembly in {"planner_only", "rah_full"}:
                event.repaired_depth = plan.repair(f"step_{index}", [f"step_{index}_retry"]).repaired_depth
            if assembly in {"memory_only", "rah_full"}:
                event.metadata["memory_hits"] = [item.text for item in memory.retrieve(task)]
        events.append(event.to_dict())
    return {
        "config": {"assembly": assembly, "seed": seed, "depth": depth, "tool_count": tool_count,
                   "mechanism_only": True},
        "events": events,
        "metrics": {"tool_calls": len(events), "failures": failures,
                    "success_rate": (depth - failures) / depth},
    }

