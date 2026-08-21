from __future__ import annotations

from itertools import product
from typing import Any


ASSEMBLIES = ("react", "planner_only", "memory_only", "safety_only", "rah_full")


def build_run_manifest(task_ids: list[str], repeats: int = 5) -> dict[str, Any]:
    if len(task_ids) != 30:
        raise ValueError("SOP-Bench protocol requires exactly 30 fixed task ids")
    runs = [
        {"run_id": f"{assembly}-{task_id}-r{repeat}", "task_id": task_id,
         "assembly": assembly, "repeat": repeat, "seed": repeat,
         "temperature": 0, "max_steps": 20}
        for task_id, assembly, repeat in product(task_ids, ASSEMBLIES, range(1, repeats + 1))
    ]
    return {
        "protocol": "rah-sopbench-v1",
        "model": "deepseek-v4-flash",
        "assemblies": list(ASSEMBLIES),
        "task_ids": task_ids,
        "repeats": repeats,
        "runs": runs,
        "exclusions": "none; failed runs are retained with their trace and failure reason",
    }

