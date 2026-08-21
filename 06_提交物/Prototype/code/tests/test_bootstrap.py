"""Prototype 无密钥复现检查的行为测试。"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest


CODE_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT))

from bootstrap import audit_demo_workspace, validate_layout  # noqa: E402


def write_json(root: pathlib.Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


class BootstrapAuditTests(unittest.TestCase):
    """改变审计判断时，这些测试必须失败。"""

    def make_demo(self) -> pathlib.Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = pathlib.Path(directory.name)
        write_json(root, "manifest.json", {"kind": "demo", "version": 1})
        write_json(root, "plan.json", {
            "reproducibility": {"seeds": [42, 43, 44]},
            "experiments": [{
                "id": "exp1",
                "type": "comparison",
                "baselines": ["no-rail", "prompt-only"],
                "ablation": "F02/F03/F04",
                "seeds": [42, 43, 44],
                "datasets": ["demo"],
                "budget": {"tokens_est": 100},
            }],
        })
        write_json(root, "experiments/exp1/results.json", {
            "metrics": {"accuracy": {"mean": 87.3}},
        })
        write_json(root, "references/references_index.json", {
            "demo2026": {"title": "Demo reference"},
        })
        paper = root / "paper" / "paper.tex"
        paper.parent.mkdir(parents=True, exist_ok=True)
        paper.write_text(
            "\\section{Results} Accuracy is 87.3\\%. \\cite{demo2026}",
            encoding="utf-8",
        )
        return root

    def test_audit_writes_passing_report_for_complete_demo(self):
        root = self.make_demo()

        report = audit_demo_workspace(root)

        self.assertTrue(report["ok"])
        self.assertEqual([], report["issues"])
        self.assertTrue((root / "audit_report.json").is_file())

    def test_audit_rejects_unverified_number(self):
        root = self.make_demo()
        (root / "paper" / "paper.tex").write_text(
            "Accuracy is 99.9\\%. \\cite{demo2026}", encoding="utf-8"
        )

        report = audit_demo_workspace(root)

        self.assertFalse(report["ok"])
        self.assertIn("99.9", " ".join(report["issues"]))

    def test_layout_rejects_missing_extension_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "custom_rails").mkdir()
            (root / "custom_skills" / "research-pipeline").mkdir(parents=True)

            report = validate_layout(root)

        self.assertFalse(report["ok"])
        self.assertIn("extensions_config.json", " ".join(report["issues"]))

    def test_bundled_prototype_layout_is_complete(self):
        """遗漏演示资产或任一核心 Rail 时，发布前检查必须失败。"""
        report = validate_layout(CODE_ROOT)

        self.assertTrue(report["ok"], report["issues"])


if __name__ == "__main__":
    unittest.main()
