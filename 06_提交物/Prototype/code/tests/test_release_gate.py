import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_gate import validate_release


class ReleaseGateTests(unittest.TestCase):
    def _write_json(self, path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def _release_root(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        result = root / "runs" / "run-001" / "results.json"
        self._write_json(result, {"metrics": {"CFR": {"mean": 0.0}}})
        paper = root / "paper.tex"
        paper.write_text("Result CFR is 0.0 \\cite{verified2026}.", encoding="utf-8")
        digest = hashlib.sha256(result.read_bytes()).hexdigest()
        self._write_json(root / "evidence_manifest.json", {
            "release_id": "v6-test",
            "status": "ready",
            "artifacts": {"runs/run-001/results.json": digest},
            "completed_runs": ["runs/run-001/results.json"],
        })
        self._write_json(root / "claims_manifest.json", {
            "claims": [{
                "claim_id": "cfr-run-001",
                "paper_text": "CFR is 0.0",
                "source_file": "runs/run-001/results.json",
                "json_path": "metrics.CFR.mean",
                "value": 0.0,
            }]
        })
        self._write_json(root / "citation_manifest.json", {
            "citations": {"verified2026": {"status": "verified", "source": "OpenAlex"}}
        })
        return root

    def test_accepts_complete_evidence_release(self) -> None:
        report = validate_release(self._release_root())
        self.assertTrue(report["ok"], report["issues"])

    def test_rejects_missing_completed_result(self) -> None:
        root = self._release_root()
        (root / "runs" / "run-001" / "results.json").unlink()
        report = validate_release(root)
        self.assertFalse(report["ok"])
        self.assertIn("missing completed result", "\n".join(report["issues"]))

    def test_rejects_unverified_paper_citation(self) -> None:
        root = self._release_root()
        (root / "paper.tex").write_text("\\cite{unverified2026}", encoding="utf-8")
        report = validate_release(root)
        self.assertFalse(report["ok"])
        self.assertIn("unverified citation", "\n".join(report["issues"]))

    def test_rejects_hash_drift(self) -> None:
        root = self._release_root()
        (root / "runs" / "run-001" / "results.json").write_text("{}", encoding="utf-8")
        report = validate_release(root)
        self.assertFalse(report["ok"])
        self.assertIn("hash mismatch", "\n".join(report["issues"]))

    def test_rejects_incomplete_collection(self) -> None:
        root = self._release_root()
        manifest_path = root / "evidence_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "collection-incomplete"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = validate_release(root)
        self.assertFalse(report["ok"])
        self.assertIn("not ready", "\n".join(report["issues"]))
