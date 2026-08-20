import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from freeze_v6_evidence import build_evidence


class FreezeEvidenceTests(unittest.TestCase):
    def test_collects_results_and_marks_unverified_citations_pending(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            result = source / "full-rail" / "seed42" / "task1" / "results.json"
            result.parent.mkdir(parents=True)
            result.write_text('{"metrics": {"CFR": {"mean": 0.0}}}', encoding="utf-8")
            paper = root / "paper.tex"
            paper.write_text("V6 evidence \\cite{source2026}.", encoding="utf-8")
            target = root / "evidence"

            manifest = build_evidence(source, paper, target, "v6-test")

            self.assertEqual(manifest["release_id"], "v6-test")
            self.assertTrue((target / "runs/full-rail/seed42/task1/results.json").is_file())
            citations = json.loads((target / "citation_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(citations["citations"]["source2026"]["status"], "pending")
            self.assertEqual(manifest["completed_runs"], ["runs/full-rail/seed42/task1/results.json"])

