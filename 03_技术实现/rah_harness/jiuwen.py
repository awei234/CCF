from __future__ import annotations

from datetime import datetime, timezone


_LAYERS = {
    "react": (),
    "planner_only": ("rah_planner",),
    "memory_only": ("rah_memory",),
    "safety_only": ("rah_safety",),
    "rah_full": ("rah_planner", "rah_memory", "rah_router", "rah_safety"),
}


def assembly_extensions(assembly: str) -> list[dict[str, object]]:
    if assembly not in _LAYERS:
        raise ValueError(f"unknown assembly: {assembly}")
    return [{"name": name, "enabled": True, "priority": 60 - index}
            for index, name in enumerate(_LAYERS[assembly])]


def build_event(run_id: str, task_id: str, assembly: str, phase: str) -> dict[str, str]:
    if assembly not in _LAYERS:
        raise ValueError(f"unknown assembly: {assembly}")
    return {"run_id": run_id, "task_id": task_id, "assembly": assembly, "phase": phase,
            "timestamp": datetime.now(timezone.utc).isoformat()}

