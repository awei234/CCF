import unittest

from rah_harness.experiments.simulator import run_synthetic
from rah_harness.experiments.sopbench import build_run_manifest


class ExperimentTests(unittest.TestCase):
    def test_synthetic_trace_is_seed_reproducible_without_method_bonuses(self):
        first = run_synthetic("rah_full", seed=42, depth=4, tool_count=6)
        second = run_synthetic("rah_full", seed=42, depth=4, tool_count=6)
        self.assertEqual(first["events"], second["events"])
        self.assertNotIn("accuracy_bonus", first["config"])
        self.assertGreaterEqual(first["metrics"]["tool_calls"], 1)

    def test_sopbench_manifest_pre_registers_750_runs(self):
        tasks = [f"domain{domain}-task{task}" for domain in range(3) for task in range(10)]
        manifest = build_run_manifest(tasks, repeats=5)
        self.assertEqual(len(manifest["runs"]), 750)
        self.assertEqual(manifest["model"], "deepseek-v4-flash")
        self.assertEqual(set(manifest["assemblies"]),
                         {"react", "planner_only", "memory_only", "safety_only", "rah_full"})

