#!/usr/bin/env python3
"""Prototype - JiuwenSwarm Research Agent Entry.

This package implements a Rail-Augmented Harness for rigorous and
self-evolving agentic research. The actual agent runtime is JiuwenSwarm;
this entry script provides a reproducible way to launch the research-pipeline
skill with the custom rails (F02/F03/F04) and to run the T1/T3 experiments
reported in the paper.

Usage:
    python main.py --stage skill      # launch the research-pipeline skill
    python main.py --stage experiment # run the T1/T3 experiment batch
    python main.py --check            # verify environment and rail loading
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import yaml

from bootstrap import audit_demo_workspace


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_env(cfg):
    required = ["jiuwenswarm", "openjiuwen"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except Exception:
            missing.append(pkg)
    if missing:
        print("[check] missing packages:", missing)
        return False
    print("[check] environment OK")
    return True


def run_skill(cfg):
    cmd = [
        cfg["runtime"]["jiuwenswarm_bin"],
        "chat",
        "使用 research-pipeline skill，自动完成科研论文全流程：选题→规划→实验→写作。",
    ]
    print("[run] ", " ".join(cmd))
    return subprocess.call(cmd)


def run_experiment(cfg):
    script = cfg["runtime"].get("experiment_script")
    if script and os.path.exists(script):
        print("[run] executing", script)
        return subprocess.call(["bash", script])
    print("[run] no experiment script configured; see run_guide.md")
    return 2


def run_demo_audit(demo_root, output=None):
    report = audit_demo_workspace(Path(demo_root), Path(output) if output else None)
    print("[demo-audit]", report)
    return 0 if report["ok"] else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(Path(__file__).with_name("config.yaml")))
    ap.add_argument("--stage", choices=["skill", "experiment", "check", "demo-audit"], default="check")
    ap.add_argument("--audit-output", default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.stage == "check":
        sys.exit(0 if check_env(cfg) else 1)
    elif args.stage == "skill":
        sys.exit(run_skill(cfg))
    elif args.stage == "experiment":
        sys.exit(run_experiment(cfg))
    elif args.stage == "demo-audit":
        output = args.audit_output or "artifacts/demo-audit.json"
        sys.exit(run_demo_audit(os.path.join(os.path.dirname(__file__), "demo"), output))


if __name__ == "__main__":
    main()
