#!/usr/bin/env python3
"""从只读实验产物建立 V6 证据包；缺失核验内容显式保留为 pending。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any


CITE_RE = re.compile(r"\\cite[a-z]*\{([^}]*)\}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _citation_keys(paper: str) -> list[str]:
    keys: list[str] = []
    for match in CITE_RE.finditer(paper):
        keys.extend(item.strip() for item in match.group(1).split(",") if item.strip())
    return list(dict.fromkeys(keys))


def build_evidence(source: Path, paper: Path, target: Path, release_id: str) -> dict[str, Any]:
    """Copy available run results into *target* and generate pending audit manifests."""
    source, paper, target = Path(source), Path(paper), Path(target)
    if not source.is_dir():
        raise ValueError(f"results source does not exist: {source}")
    if not paper.is_file():
        raise ValueError(f"paper does not exist: {paper}")
    target.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, str] = {}
    completed_runs: list[str] = []
    for result in sorted(source.rglob("results.json")):
        relative = result.relative_to(source)
        destination = target / "runs" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result, destination)
        key = destination.relative_to(target).as_posix()
        artifacts[key] = _sha256(destination)
        completed_runs.append(key)

    paper_destination = target / "paper.tex"
    shutil.copy2(paper, paper_destination)
    artifacts["paper.tex"] = _sha256(paper_destination)
    _write_json(target / "evidence_manifest.json", {
        "release_id": release_id,
        "status": "collection-incomplete",
        "source_type": "real_model_run",
        "source_results_root": str(source),
        "artifacts": artifacts,
        "completed_runs": completed_runs,
        "known_gaps": [
            "claims_manifest must map every release claim to a run metric before release validation can pass",
            "citation_manifest entries must be independently verified before release validation can pass",
            "this collection contains only result files available under the supplied source directory",
        ],
    })
    _write_json(target / "claims_manifest.json", {"claims": []})
    _write_json(target / "citation_manifest.json", {
        "citations": {
            key: {"status": "pending", "source": None, "checked_at": None}
            for key in _citation_keys(paper_destination.read_text(encoding="utf-8"))
        }
    })
    return _load_manifest(target)


def _load_manifest(target: Path) -> dict[str, Any]:
    return json.loads((target / "evidence_manifest.json").read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--paper", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--release-id", default="v6")
    args = parser.parse_args()
    manifest = build_evidence(args.source, args.paper, args.target, args.release_id)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
