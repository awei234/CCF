import unittest

from rah_harness.jiuwen import assembly_extensions, build_event


class JiuwenAdapterTests(unittest.TestCase):
    def test_full_assembly_registers_all_four_rah_layers(self):
        names = [item["name"] for item in assembly_extensions("rah_full")]
        self.assertEqual(names, ["rah_planner", "rah_memory", "rah_router", "rah_safety"])

    def test_react_assembly_registers_no_rah_extension(self):
        self.assertEqual(assembly_extensions("react"), [])

    def test_lifecycle_event_includes_assembly_and_run_identity(self):
        event = build_event("run-7", "task-9", "rah_full", "before_tool_call")
        self.assertEqual(event["run_id"], "run-7")
        self.assertEqual(event["phase"], "before_tool_call")

