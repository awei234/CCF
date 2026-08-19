#!/usr/bin/env python3
"""无密钥 Prototype 复现检查与 demo 审计入口。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
CITE_RE = re.compile(r"\\cite[a-z]*\{([^}]*)\}")
NUMBER_RE = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _numbers(value: Any) -> set[float]:
    if isinstance(value, bool):
        return set()
    if isinstance(value, (int, float)):
        return {round(float(value), 2)}
    if isinstance(value, dict):
        return set().union(*(_numbers(item) for item in value.values())) if value else set()
    if isinstance(value, list):
        return set().union(*(_numbers(item) for item in value)) if value else set()
    return set()


def validate_layout(root: Path) -> dict[str, Any]:
    """检查可复现包必须随包提供的扩展与 demo 资源。"""
    expected = [
        "extensions_config.json",
        "custom_skills/research-pipeline/SKILL.md",
        "custom_rails/experiment_planning_rail/rail.py",
        "custom_rails/result_consistency_rail/rail.py",
        "custom_rails/citation_verification_rail/rail.py",
        "demo/manifest.json",
    ]
    missing = [item for item in expected if not (root / item).is_file()]
    return {"ok": not missing, "issues": [f"missing required file: {item}" for item in missing]}


def audit_demo_workspace(root: Path, output: Path | None = None) -> dict[str, Any]:
    """对明确标识为 demo 的最小工作区做离线审计。"""
    issues: list[str] = []
    manifest = _load_json(root / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("kind") != "demo":
        issues.append("manifest.json must declare kind=demo")

    plan = _load_json(root / "plan.json")
    experiments = plan.get("experiments") if isinstance(plan, dict) else None
    if not isinstance(plan, dict) or not plan.get("reproducibility"):
        issues.append("plan.json is missing reproducibility metadata")
    if not isinstance(experiments, list) or not experiments:
        issues.append("plan.json is missing experiments")
    else:
        for experiment in experiments:
            experiment_id = experiment.get("id", "unknown") if isinstance(experiment, dict) else "unknown"
            if not isinstance(experiment, dict) or len(experiment.get("baselines", [])) < 2:
                issues.append(f"{experiment_id}: fewer than two baselines")
            if not isinstance(experiment, dict) or not experiment.get("ablation"):
                issues.append(f"{experiment_id}: missing ablation")

    result_values: set[float] = set()
    for result_path in root.glob("experiments/**/results.json"):
        result = _load_json(result_path)
        if result is None:
            issues.append(f"invalid result file: {result_path.relative_to(root)}")
        else:
            result_values |= _numbers(result)
    if not result_values:
        issues.append("no numeric values found in results.json")

    reference_index = _load_json(root / "references" / "references_index.json")
    reference_keys = set(reference_index) if isinstance(reference_index, dict) else set()
    paper_path = root / "paper" / "paper.tex"
    paper = paper_path.read_text(encoding="utf-8") if paper_path.is_file() else ""
    if not paper:
        issues.append("missing paper/paper.tex")
    else:
        for number in NUMBER_RE.findall(CITE_RE.sub("", paper)):
            if round(float(number), 2) not in result_values:
                issues.append(f"unverified numeric claim: {number}")
        for match in CITE_RE.finditer(paper):
            for key in (item.strip() for item in match.group(1).split(",")):
                if key and key not in reference_keys:
                    issues.append(f"unverified citation: {key}")

    report = {
        "kind": "demo-audit",
        "demo_only": True,
        "ok": not issues,
        "issues": issues,
        "result_value_count": len(result_values),
    }
    report_path = output or root / "audit_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate bundled extension and demo resources")
    parser.add_argument("--demo-audit", action="store_true", help="audit the bundled demo workspace")
    parser.add_argument("--root", type=Path, default=PACKAGE_ROOT, help="Prototype code root")
    parser.add_argument("--output", type=Path, help="path for demo audit report")
    args = parser.parse_args()

    if not args.check and not args.demo_audit:
        parser.error("choose --check and/or --demo-audit")
    ok = True
    if args.check:
        layout = validate_layout(args.root)
        print(json.dumps(layout, ensure_ascii=False))
        ok = ok and layout["ok"]
    if args.demo_audit:
        report = audit_demo_workspace(args.root / "demo", args.output)
        print(json.dumps(report, ensure_ascii=False))
        ok = ok and report["ok"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
