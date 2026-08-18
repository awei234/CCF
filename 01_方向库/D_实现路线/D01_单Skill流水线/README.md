# D01 单 Skill 流水线（官方基本思路）

> 分组：D 实现路线 ｜ 难度 ★★☆ ｜ 成本 低 ｜ 推荐度 ★★★☆
> 状态：待开发（阶段 1 阶段任务）｜ 更新日期：2026-08-11

---

## 1. 方向定义

在 JiuwenSwarm 中**新建一个科研 skill**，把论文自动化全流程（选题拆解 → 文献调研 → 方法设计 → 论文撰写 → 结果分析）写进该 skill 的 SKILL.md 与脚本里，Agent 按 skill 指引逐步完成。

这是官方点名的**基本思路**："基于 JiuwenSwarm，通过单个 skill 或 team skill 实现论文自动化生成"。

## 2. 为什么选

- **启动最快**：不碰源码，skill 机制是现成的（框架自带 21 个 skill 可参照），阶段 1 就能出第一篇论文
- **合规基线**：满足"基于 openJiuwen 开源代码开发"，先拿到 SAR 基线分
- **是 D03/D05 的地基**：流水线的 prompt、工具、流程先在这里跑通，再迁移到 rail 管控

## 3. 可行性分析

| 项 | 分析 |
|---|---|
| 框架支持 | ✅ JiuwenSwarm skill 机制成熟（SKILL.md + references/ + scripts/，渐进式披露）|
| 参照模板 | ✅ `03_技术实现/jiuwenswarm/jiuwenswarm/resources/agent/workspace/skills/skill-omni-creation/`、`ppt-creation/` |
| 四阶段 prompt | ✅ FARS 论文附录 B 完整原文（`02_情报库/FARS标杆分析/fars_paper_text.txt`）可直接复用 |
| 模型 | ✅ DeepSeek OpenAI 兼容接口 |
| 风险 | ⚠️ 纯 skill 方案与官方"进阶思路"（改 rail）拉开差距的潜力有限 |

## 4. 所需源码改动点

- 无需改 JiuwenSwarm 源码（skill 是纯新增资源）→ 放在 `03_技术实现/custom_skills/research-pipeline/`
- 若需注册进框架的 skill 目录，可把 skill 放 `resources/agent/workspace/skills/`（这本身算"改动源码目录"）

## 5. 对应评分维度

写作清晰度（10%）+ 相关工作完整性（10%）——**决定 SAR 下限**

## 6. 优先级

**阶段 1 最高**（先出基线），长期降级为 D05 的一个组件。

## 7. 参考依据

- FARS 附录 B 四阶段 prompt（Ideation/Plan/Experiment/Writing 指南）
- 框架内置 skill 范例（skill-omni-creation、doc-update）
- `docs/zh/技能.md`（Agent Skill 机制）

## 8. 待办清单

- [ ] 建 skill 目录结构（SKILL.md + prompts/ + scripts/）
- [ ] 把 FARS 附录 B 四阶段 prompt 翻译/适配成中文 skill 指引
- [ ] 配置 DeepSeek 驱动
- [ ] 端到端跑通第一篇论文
- [ ] 提交 SAR 拿基线分（→ 05_评测与迭代/基线分.md）
