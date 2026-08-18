# F01 写作质量 Rail（SAR 下限保障）

> 分组：F 功能模块 ｜ 实现成本 低 ｜ 影响维度：写作清晰度 10%（下限保障）
> 状态：阶段 4 开发 ｜ 更新日期：2026-08-11

---

## 1. 模块定义

一个自定义 rail，在**写作阶段**对论文草稿做结构化硬校验，确保达到 SAR 高分画像的硬性指标——词数、图表密度、复杂度分析、结构完整性、格式合规。

**一句话**：论文质量不靠 agent 自觉，靠 rail 卡指标。

## 2. 为什么重要

- SAR 高分画像（Claude Code vs Kimi 差异实证）：
  - 词数 4,023 vs 2,461（差 1.2 分）
  - 图 4.8 vs 0.8、表 6.0 vs 4.0
  - 含复杂度分析 77% vs 64%
- 写作质量决定 SAR 下限：下限高，六维均衡拿分

## 3. 功能规格（硬校验清单）

| 校验项 | 阈值 | 说明 |
|---|---|---|
| 词数 | ≥ 4,000 词 | 短论文标准 |
| 图数量 | ≥ 4 张 | 每图有数据来源（F03 联动）|
| 表数量 | ≥ 6 张 | 同上 |
| 复杂度分析 | 必须含 | 算法/系统复杂度 O() 分析章节 |
| 结构完整 | 必须含 | Abstract/Intro/Method/Experiments/Discussion/Conclusion/Related Work |
| 图表规范 | LaTeX 合规 | ICLR 模板格式、caption 齐全 |
| 引用合规 | 25-40 篇 | F04 联动核验 |
| 负结果 | 建议含 | SAR 给诚实负结果加分（可选加分项）|

## 4. 实现要点

```python
class WritingQualityRail(DeepAgentRailBase):
    priority = 800
    def after_model_call(self, ctx):
        report = check_paper_metrics(ctx.output)   # 词数/图表/结构/复杂度
        if not report.pass_all():
            return quality_fix_guide(report)       # 引导补齐短板
```

## 5. 挂载方式

- 写作阶段 rail：`03_技术实现/jiuwenswarm/jiuwenswarm/agents/harness/code/rails/writing_quality_rail.py`
- 配套检查脚本：`tools/paper_metrics.py`（LaTeX 解析：词数/图表数/章节）

## 6. 验收标准

- [ ] 输出论文自动满足全部阈值
- [ ] 指标检查脚本与人工核对一致（抽查 2 篇）
- [ ] 与 F03/F04 联动无冲突

## 7. 参考依据

- FARS 评测论文 Table 1 + §4.2 研究人格分析（高分画像）
- ICLR 模板规范（04_论文写作/）
- FARS 附录 B Writing 指南

## 8. 待办清单

- [ ] 实现 paper_metrics.py（LaTeX 解析）
- [ ] 实现 rail 校验 + 补齐引导
- [ ] 单测（短文/缺图/缺复杂度场景）
- [ ] 挂载 + 端到端验证
