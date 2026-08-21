"""Prototype 主入口的失败码契约测试。"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest


CODE_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT))

from main import run_demo_audit, run_experiment  # noqa: E402


class MainEntryTests(unittest.TestCase):
    def test_missing_experiment_script_returns_nonzero(self):
        """若缺少实验脚本仍返回 0，调用方会误判复现成功。"""
        result = run_experiment({"runtime": {"experiment_script": "missing.sh"}})

        self.assertNotEqual(result, 0)

    def test_demo_audit_returns_zero_and_writes_report(self):
        """无密钥 demo 审计成功时，CLI 阶段必须返回成功码并产出报告。"""
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "report.json"

            result = run_demo_audit(CODE_ROOT / "demo", output)

            self.assertEqual(result, 0)
            self.assertTrue(output.is_file())

    def test_demo_audit_cli_accepts_output_path(self):
        """命令行传入输出路径时，demo 阶段必须能正常审计并退出。"""
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "report.json"
            completed = subprocess.run(
                [sys.executable, "main.py", "--stage", "demo-audit", "--audit-output", str(output)],
                cwd=CODE_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(output.is_file())

    def test_demo_audit_cli_works_outside_code_directory(self):
        """从仓库根目录调用入口时，不应因相对 config.yaml 路径失败。"""
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "report.json"
            completed = subprocess.run(
                [str(sys.executable), str(CODE_ROOT / "main.py"), "--stage", "demo-audit", "--audit-output", str(output)],
                cwd=CODE_ROOT.parents[2],
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
