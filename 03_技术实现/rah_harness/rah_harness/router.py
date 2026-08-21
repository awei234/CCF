from __future__ import annotations

import re
from dataclasses import dataclass

from .core import ToolSpec


@dataclass(frozen=True)
class RouteDecision:
    tool: ToolSpec
    score: float


def _terms(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", value.lower()))


def route_tool(task: str, tools: list[ToolSpec], cost_weight: float = 0.1) -> RouteDecision:
    task_terms = _terms(task)
    ranked: list[RouteDecision] = []
    for tool in tools:
        relevance = len(task_terms & _terms(f"{tool.name} {tool.description}"))
        reversibility_bonus = 0.01 if tool.reversible else 0.0
        ranked.append(RouteDecision(tool, relevance - cost_weight * tool.estimated_cost + reversibility_bonus))
    if not ranked:
        raise ValueError("at least one tool is required")
    return sorted(ranked, key=lambda decision: (-decision.score, decision.tool.name))[0]

