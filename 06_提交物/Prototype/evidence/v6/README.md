# V6 真实证据收集状态

本目录由 `code/freeze_v6_evidence.py` 从 `.zcode/tools/exp1` 的现存结果建立。

- 当前状态：`collection-incomplete`，**不得作为已冻结 V6 发布包或实验结论的唯一证据**。
- 已归档：21 份可发现的 T1/T2 逐 seed `results.json` 与 V6 `paper.tex`，全部列入 `evidence_manifest.json` 的 SHA-256 清单。
- 未归档：可追溯的 T3 原始结果、逐声明 `claims_manifest`、独立引用核验记录，以及 release-ready 版本状态。
- `release_gate.py` 会拒绝该目录，直到所有缺口补齐并将 manifest 状态改为 `ready`。

V7 脚本或结果不得写入此目录。
