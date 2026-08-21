from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepairResult:
    repaired_depth: int


class PlanTree:
    def __init__(self, children: dict[str, list[str]], parent: dict[str, str]) -> None:
        self._children = children
        self._parent = parent

    @classmethod
    def from_paths(cls, paths: list[tuple[str, ...]]) -> "PlanTree":
        children: dict[str, list[str]] = {}
        parent: dict[str, str] = {}
        for path in paths:
            for node, child in zip(path, path[1:]):
                children.setdefault(node, [])
                if child not in children[node]:
                    children[node].append(child)
                children.setdefault(child, [])
                parent[child] = node
        return cls(children, parent)

    def children_of(self, node: str) -> tuple[str, ...]:
        return tuple(self._children.get(node, []))

    def repair(self, failed_node: str, replacement_children: list[str]) -> RepairResult:
        if failed_node not in self._children:
            raise ValueError(f"unknown plan node: {failed_node}")
        previous = self._children[failed_node]
        for child in previous:
            self._drop_descendants(child)
            self._parent.pop(child, None)
        self._children[failed_node] = list(replacement_children)
        for child in replacement_children:
            self._children.setdefault(child, [])
            self._parent[child] = failed_node
        return RepairResult(repaired_depth=2 if previous or replacement_children else 1)

    def _drop_descendants(self, node: str) -> None:
        for child in self._children.get(node, []):
            self._drop_descendants(child)
            self._parent.pop(child, None)
        self._children.pop(node, None)

