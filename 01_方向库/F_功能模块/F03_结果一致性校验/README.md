# F03 结果一致性校验 Rail（第一批核心）★

> 分组：F 功能模块 ｜ 实现成本 中 ｜ 影响维度：实验严谨性 15% + 决赛复现生命线
> 状态：阶段 2 开发 ｜ 更新日期：2026-08-11

---

## 1. 模块定义

一个自定义 rail，在**写作阶段**强制论文中的每个数字/结论必须能在实验产物（`results.json`）中找到一一对应的出处——从机制上杜绝"捏造结果"（全场最高 77% 中招率）。

**一句话**：论文里出现的每个数，都必须有结果文件兜底；查不到就不许写。

## 2. 为什么是第一批

- 捏造结果是三大失败模式中最致命的（Codex 5%/8% vs Kimi 77%/72%，15 倍差距；Claude Code 也偶发 31%）
- SAR "不核实实验实质"——但**决赛复现审核会核实**；论文数字与 artifact 一致是决赛不翻车的生命线
- 实现可控：字符串/数值匹配逻辑，无外部依赖

## 3. 功能规格

### 3.1 校验机制（写作 rail）

| 校验项 | 规则 |
|---|---|
| 数字提取 | 从论文草稿提取所有数值型论断（精度/指标/对比）|
| 来源匹配 | 每个数字必须在 `results.json` 树中找到匹配键值（允许推导：如从原始值算出的均值/方差）|
| 表格一致性 | 论文表格单元格逐项对应 results 文件 |
| 图表数据 | 论文图的原始数据可追溯到 results 文件 |
| 引用一致性 | 论文声称"实现了 X 组件"必须有对应代码/产物文件（F04 联动）|

### 3.2 失败动作

- 写作 rail 拦截输出，给出"未验证数字清单"让 agent 修正（改数字或补实验）
- 可选：`before_tool_call` 在写入 tex 前校验；`after_model_call` 校验生成文本

### 3.3 产物协议（贯穿 F02→F03）

```
workspace/
├── plan.json              # F02 规划产物
├── experiments/
│   ├── exp1/
│   │   ├── config.json
│   │   ├── results.json   # F03 校验的数据源
│   │   └── logs/
│   └── exp2/ ...
└── paper/
    ├── paper.tex          # 写作产物（F03 校验对象）
    └── figures/           # 图表（数据来源可追溯）
```

## 4. 实现要点

```python
class ResultConsistencyRail(DeepAgentRailBase):
    priority = 850
    def after_model_call(self, ctx):      # 校验生成的论文文本
        numbers = extract_numeric_claims(ctx.output)
        unmatched = [n for n in numbers if not verify_in_results(n, ctx.workspace)]
        if unmatched:
            return rewrite_guide(unmatched)   # 引导修正
```

## 5. 挂载方式

- 放 `03_技术实现/jiuwenswarm/jiuwenswarm/agents/harness/code/rails/result_consistency_rail.py`
- 与 F02 组合使用（F02 管计划、F03 管报告）

## 6. 验收标准

- [ ] 论文含伪造数字时 rail 能识别并拦截
- [ ] 论文数字与 results.json 完全一致时放行
- [ ] 生成的图/表数据可追溯（图数据文件抽查）
- [ ] 全流水线跑完的论文 0 捏造

## 7. 参考依据

- FARS 附录 B Writing 指南："论文数字必须与 results.json 逐字一致、明令禁止捏造"
- FARS 评测论文 §5.2（捏造模式分析）
- `docs/zh/Harness.md`（改写 tool_result 的 rail 能力）

## 8. 待办清单

- [ ] 定义 results.json 标准 schema
- [ ] 实现数字提取 + 来源匹配引擎
- [ ] 实现未验证数字清单的修正引导
- [ ] 单测（伪造数字/合法数字场景）
- [ ] 挂载 + 端到端验证
