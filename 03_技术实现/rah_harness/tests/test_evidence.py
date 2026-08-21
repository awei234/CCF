import unittest

from rah_harness.evidence import validate_run_record


class EvidenceTests(unittest.TestCase):
    def test_accepts_complete_real_run_record(self):
        record = {
            "run_id": "rah_full-aircraft_inspection-000-r1", "task_id": "aircraft_inspection:000",
            "assembly": "rah_full", "model": "deepseek-v4-flash", "terminal_status": "success",
            "trace_path": "traces/run.jsonl", "token_usage": 123, "latency_seconds": 4.2,
            "api_cost_usd": 0.01,
        }
        self.assertEqual(validate_run_record(record), [])

    def test_rejects_record_without_trace_or_cost(self):
        issues = validate_run_record({"run_id": "r1"})
        self.assertIn("missing trace_path", issues)
        self.assertIn("missing api_cost_usd", issues)

