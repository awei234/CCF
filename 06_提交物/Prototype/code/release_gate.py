#!/usr/bin/env python3
"""V6 冻结证据的确定性发布验收入口。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


CITE_RE = re.compile(r"\\cite[a-z]*\{([^}]*)\}")


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _read_path(value: Any, dotted_path: str) -> Any:
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_release(root: Path) -> dict[str, Any]:
    """Validate a self-contained evidence directory without mutating it."""
    root = Path(root)
    issues: list[str] = []
    evidence = _load_json(root / "evidence_manifest.json")
    claims = _load_json(root / "claims_manifest.json")
    citations = _load_json(root / "citation_manifest.json")
    paper_path = root / "paper.tex"

    if not evidence or not evidence.get("release_id"):
        issues.append("missing evidence_manifest.json release_id")
        evidence = {}
    elif evidence.get("status") != "ready":
        issues.append(f"evidence manifest not ready: {evidence.get('status', 'missing status')}")
    if not claims or not isinstance(claims.get("claims"), list):
        issues.append("missing claims_manifest.json claims")
        claims = {"claims": []}
    if not citations or not isinstance(citations.get("citations"), dict):
        issues.append("missing citation_manifest.json citations")
        citations = {"citations": {}}
    paper = paper_path.read_text(encoding="utf-8") if paper_path.is_file() else ""
    if not paper:
        issues.append("missing paper.tex")

    artifacts = evidence.get("artifacts", {})
    if not isinstance(artifacts, dict):
        issues.append("artifacts must be an object")
        artifacts = {}
    for relative_path, expected_hash in artifacts.items():
        artifact = root / relative_path
        if not artifact.is_file():
            issues.append(f"missing artifact: {relative_path}")
        elif _sha256(artifact) != expected_hash:
            issues.append(f"hash mismatch: {relative_path}")

    completed_runs = evidence.get("completed_runs", [])
    if not isinstance(completed_runs, list):
        issues.append("completed_runs must be a list")
        completed_runs = []
    for relative_path in completed_runs:
        if not isinstance(relative_path, str) or not (root / relative_path).is_file():
            issues.append(f"missing completed result: {relative_path}")

    for claim in claims["claims"]:
        if not isinstance(claim, dict):
            issues.append("invalid claim entry")
            continue
        for field in ("claim_id", "paper_text", "source_file", "json_path", "value"):
            if field not in claim:
                issues.append(f"claim missing {field}: {claim.get('claim_id', 'unknown')}")
        source = root / str(claim.get("source_file", ""))
        if claim.get("paper_text") not in paper:
            issues.append(f"claim text absent from paper: {claim.get('claim_id', 'unknown')}")
        source_data = _load_json(source)
        actual = _read_path(source_data, str(claim.get("json_path", ""))) if source_data else None
        if actual != claim.get("value"):
            issues.append(f"claim source mismatch: {claim.get('claim_id', 'unknown')}")

    citation_entries = citations["citations"]
    for match in CITE_RE.finditer(paper):
        for key in (item.strip() for item in match.group(1).split(",")):
            entry = citation_entries.get(key) if key else None
            if not isinstance(entry, dict) or entry.get("status") != "verified":
                issues.append(f"unverified citation: {key}")

    return {
        "kind": "release-gate-report",
        "release_id": evidence.get("release_id"),
        "ok": not issues,
        "issues": issues,
        "artifact_count": len(artifacts),
        "claim_count": len(claims["claims"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="frozen evidence directory")
    parser.add_argument("--output", type=Path, help="optional report path")
    args = parser.parse_args()
    report = validate_release(args.root)
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    print(encoded)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
