# SAR 反馈分析（v2/v3 评语 → 阶段 3 入口）

> 更新：2026-08-15（v3 出分 5.8 后补充）· 数据源：SAR结果_v2.json（5.2）+ SAR结果_v3.json（5.8）
> 用法：阶段 3 每次迭代从本表选 1-2 个修改点（细化_01 阶段 3 任务 1）

## 〇、v3 修复闭环结果

| 项 | v2 | v3 | 说明 |
|---|---|---|---|
| Writing_Clarity | 0 | **+1** | 表格 fit + 实现细节段 + Code 段直接生效 |
| 总分 | 5.2 | **5.8** | +0.6，回到 v1 水平 |

## 一、已闭环项（v3 修复轮）

| # | 评语问题 | v3 修复 | 状态 |
|---|---|---|---|
| 1 | Writing_Clarity：表格渲染 artifacts | 全部表格 `\resizebox` 缩放进栏宽（Overfull 9→1.25pt）；caption 长路径缩短 | ✅ 已提交 v3 |
| 2 | 实现细节不足（railbench 任务/验证实现） | 新增 Implementation details 段（prompt 指令 3 条原文、核验器短语搜索+阈值、NFR 四分类、审计文件清单）| ✅ |
| 3 | 代码/数据可用性未声明 | 新增 Code & Data Availability 段（提交包目录 + jiuwenswarm PR）| ✅ |
| 4 | F03 提取器对 preamble 参数误报 | strip_latex 剥孤立参数块（\documentclass[10pt]、\newcommand{\fit}[1]），单测 16/16 | ✅ |

## 二、阶段 3 候选修改点（按 ROI 排序）

| 优先级 | 修改点 | 回应评语 | 成本 | 落点 |
|---|---|---|---|---|
| P0 | **独立验证打破循环**（v3 新点名）：人工抽样审计（30-50 数字/引用）+ inter-rater；ambiguous coverage 指标（CFR 分母补不确定度）| 「circularity risk」「audit is not independent of enforcement」| 中 | 阶段 3 全程 |
| P0 | **开放池写作任务（E2）**：引用不预核验、池开放，放大捏造空间测 CFR 区分度 | 「extreme floor effects」「external validity weak」| 中（新任务池 + 3 臂 × seeds）| 阶段 3 E2 |
| P0 | **no-rail T1 完整重跑**：消除重建控制组（现为 summary_E1 重建）| 「reconstructed control run weakens all-equal claim」| 低（1 会话重跑 T1）| 阶段 3 E1 补 |
| P1 | **单门控消融**：f02-only / f03-only / f04-only + 两两组合 | 「No ablations of individual gates」+ 问题 5 | 中（6 臂 × 任务 × seeds）| 阶段 3 E1 注册臂 |
| P1 | **faithfulness 核验（F04b）**：抽样用 CiteAudit 式 claim-level support 判定，报告支持率 | 问题 2「citation faithfulness beyond existence」| 中（LLM 抽样审计）| 阶段 3 E2 |
| P1 | **多模型**：至少 2 个模型家族（deepseek-v4-flash + 另一模型）| 问题 5「two model families」| 中（模型切换）| 阶段 3 E3 |
| P2 | **成本核算**：runtime/latency/金钱成本（非仅 tiktoken 估算）+ 按打回轮分解 | 问题 4 | 低（日志统计）| 阶段 3 全程 |
| P2 | **NFR 分类收紧**：pre-registered constants vs assumed settings 二分 + justification | 问题 3「self-declared design parameters 太宽松」| 低（分类器改）| 阶段 3 |
| P2 | **人工审计抽样**：数字/声称提取器的 precision/recall（30-50 条抽样）| 问题 6「human audit of extraction」| 低 | 阶段 3 |
| P3 | **detector 集成对比**：F04 存在性 + CiteAudit  faithfulness 联合；新名单 clibib/SemanticCite/HalluCiteChecker/SafeGate/AutoVerifier | 「testing rails in tandem with detectors」| 中 | 阶段 4 |
| P3 | **related work 扩展**：FACTUM/PaperOrchestra/HLER/AutoPyVerifier/FIRE/FinVet | 「missing related work」| 低（写作）| v4 |

## 三、v2 保留优势（不可丢）

- 三臂同 seed 配对设计（评语明确肯定）
- 门控-指标同构（measurement is auditing）
- 门控行为证据（F02 拦截、打回计数）
- 诚实披露文化（v3 已再加 Implementation/Code 段）
