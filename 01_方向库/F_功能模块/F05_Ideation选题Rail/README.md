# F05 Ideation 选题 Rail（研究重要性保障）

> 分组：F 功能模块 ｜ 实现成本 中 ｜ 影响维度：研究重要性 20%
> 状态：阶段 5+ 开发（第三批）｜ 更新日期：2026-08-11

---

## 1. 模块定义

一个 rail/流程，在**选题阶段**引导 Agent 生成高质量研究假设，并做 novelty 三步验证与筛选，解决 FARS 局限 4"复杂假设筛选能力弱"。

**一句话**：选题是研究重要性（20%）的唯一决定因素，用流程保证选题质量。

## 2. 为什么重要

- 研究重要性维度权重 20%（8 分），是 SAR 六维中**唯一完全靠选题/叙事**的维度
- FARS 局限 4 明确"能生成大量假设，但筛选高价值复杂假设能力不足"
- 选题一旦错了，后面 rail 再强也救不回重要性分

## 3. 功能规格（沿用 FARS 附录 B Ideation 指南）

### 3.1 选题方法论
- Schulman 建议的选题标准（问题重要 + 有人在意 + 我们能解决）
- 从"官方建议主题 + 文献空白"两个来源生成候选主题

### 3.2 novelty 三步验证（rail 强制）
1. 检索验证：该 idea 是否已有工作（Semantic Scholar / arXiv 检索）
2. 差异验证：与最相近 3 篇工作的差异点是否成立
3. 可行性验证：以现有资源（模型/算力/数据）是否可完成实验

### 3.3 输出协议
```
proposal.md   # 研究提案（问题/动机/方法/预期贡献/风险）
idea.json     # 结构化 idea（主题/novelty 声明/相关 work 列表）
references/   # 调研文献（进 F04 引用池）
```

### 3.4 假设筛选
- 候选主题必须过 novelty 三步验证才放行到 plan 阶段
- 多候选时按"新颖度 × 可行性 × 与主线契合度"排序

## 4. 实现要点

- 可在 skill 层实现（提示词流程）或 rail 层实现（强制校验 proposal 完整性）
- 检索部分复用 `openJiuwen-DeepSearch` 内置 skill 或直接调 Semantic Scholar API
- 与 F04 联动：references/ 目录直接成为引用候选池

## 5. 挂载方式

- skill 流程：`03_技术实现/custom_skills/research-pipeline/prompts/ideation/`
- rail：`code/rails/ideation_quality_rail.py`（校验 proposal.md/idea.json 完整性 + novelty 证据）

## 6. 验收标准

- [ ] 选题有明确的文献空白依据（检索证据）
- [ ] idea.json 完整（novelty 声明有对照工作）
- [ ] 选题通过后进入 plan 阶段无返工

## 7. 参考依据

- FARS 附录 B Ideation 指南（Schulman 建议、novelty 三步验证、proposal/idea/references 结构）
- `docs/zh/技能.md`（skill 机制）

## 8. 待办清单

- [ ] 梳理 Ideation 提示词（从 FARS 附录 B 提取）
- [ ] 实现 novelty 检索验证脚本
- [ ] 定义 proposal.md/idea.json 模板
- [ ] （可选）实现 rail 强制校验
