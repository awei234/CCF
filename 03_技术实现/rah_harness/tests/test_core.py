import unittest

from rah_harness.core import (
    ExpectedSignature,
    ExecutionEvent,
    ToolSpec,
    validate_tool_call,
)
from rah_harness.memory import BM25Memory
from rah_harness.planner import PlanTree
from rah_harness.router import route_tool


class RAHCoreTests(unittest.TestCase):
    def test_blocks_missing_required_argument_before_irreversible_tool_call(self):
        tool = ToolSpec(
            name="submit_report",
            description="Submit a report to the external service.",
            required_args=("report_id",),
            estimated_cost=2.0,
            reversible=False,
            permission="external_write",
        )
        event = validate_tool_call(tool, {}, ExpectedSignature(required_fields=("accepted",)))
        self.assertTrue(event.blocked)
        self.assertEqual(event.failure_reason, "missing required arguments: report_id")

    def test_bm25_returns_relevant_episode_deterministically(self):
        memory = BM25Memory(capacity=3, top_k=1)
        memory.add("A database query timed out after selecting search_db.")
        memory.add("A report was submitted successfully.")
        self.assertEqual(memory.retrieve("database query timeout")[0].text,
                         "A database query timed out after selecting search_db.")

    def test_router_prefers_relevant_reversible_tool_when_costs_tie(self):
        tools = [
            ToolSpec("delete_dataset", "delete dataset permanently", (), 1.0, False, "destructive"),
            ToolSpec("inspect_dataset", "inspect dataset schema", (), 1.0, True, "read"),
        ]
        decision = route_tool("inspect the dataset schema", tools)
        self.assertEqual(decision.tool.name, "inspect_dataset")

    def test_plan_repair_only_replaces_failed_subtree(self):
        plan = PlanTree.from_paths([("root", "a", "a1"), ("root", "b", "b1")])
        repaired = plan.repair("a", ["a2", "a3"])
        self.assertEqual(repaired.repaired_depth, 2)
        self.assertEqual(plan.children_of("b"), ("b1",))
        self.assertEqual(plan.children_of("a"), ("a2", "a3"))

    def test_execution_event_serializes_trace_fields(self):
        event = ExecutionEvent(task_id="task-1", run_id="run-1", tool="inspect_dataset")
        self.assertEqual(event.to_dict()["task_id"], "task-1")

