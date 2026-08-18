# F07 图表生成模块（写作质量增强）

> 分组：F 功能模块 ｜ 实现成本 中 ｜ 影响维度：写作清晰度 10%（图表密度信号）
> 状态：阶段 4 开发（第二批）｜ 更新日期：2026-08-11

---

## 1. 模块定义

自动生成论文图表（matplotlib / LaTeX TikZ），并保证**图有数据来源、表可追溯**，把 SAR 的"图表密度"信号做满（目标 4-5 图 + 6 表）。

**一句话**：图表的"多"和"规范"是 SAR 强信号，用脚本批量生成而不是靠 agent 手搓。

## 2. 为什么重要

- 实证：Claude Code 4.8 图/6.0 表 vs Kimi 0.8 图/4.0 表，SAR 分差 1.2（写作维度 4 分里影响巨大）
- 图表规范直接进"写作清晰度"与"实验严谨性"双维度
- 框架自带 `ppt-creation` skill 支持论文原图——可复用其图表管线思路

## 3. 功能规格

### 3.1 图表类型（自动生成）
| 类型 | 用途 | 数据来源 |
|---|---|---|
| 实验对比图（bar/line）| baseline 对比 | results.json |
| 消融图 | ablation 结果 | results.json |
| 收敛曲线 | 训练/推理过程 | logs |
| 复杂度分析图 | O() 对比 | 理论计算 |
| 系统架构图 | 方法展示 | 定义文件 |
| 表格（LaTeX）| 全量结果/消融/成本 | results.json |

### 3.2 生成流程
1. 从 results.json 抽取数据 → 2. 脚本生成 figure/table → 3. caption 自动填充（含数据说明）→ 4. F03 校验数据一致性 → 5. 嵌入 tex

### 3.3 质量要求
- 每图有数据来源注释（可追溯 = F03 联动）
- 统一风格（字体/配色/尺寸，符合 ICLR 模板）
- 高 DPI（300+）保证 PDF 清晰

## 4. 实现要点

- 工具：`tools/figure_generator.py`（matplotlib）+ `tools/table_generator.py`（LaTeX）
- 图表配置文件：`config/figure_style.yaml`（统一风格）
- 复用：`03_技术实现/jiuwenswarm/jiuwenswarm/resources/agent/workspace/skills/ppt-creation/` 的图表管线思路
- 可选：rail 检查图表数量/来源（并入 F01 的 paper_metrics）

## 5. 挂载方式

- 独立工具模块 + 在写作阶段 skill 流程中调用
- 图表数量校验并入 F01 writing_quality_rail

## 6. 验收标准

- [ ] 每篇论文自动产出 ≥4 图 + ≥6 表
- [ ] 每图数据可追溯到 results.json（F03 抽查）
- [ ] 图表符合 ICLR 模板视觉规范

## 7. 参考依据

- FARS 评测论文 §4.2（图表密度与分数相关）
- `ppt-creation` skill（论文原图管线）
- ICLR 模板图表规范（04_论文写作/）

## 8. 待办清单

- [ ] 实现 figure_generator.py + table_generator.py
- [ ] 定义图表风格配置
- [ ] 与 F03 数据源打通
- [ ] 接入写作流水线
- [ ] 抽样人工核对图表质量
