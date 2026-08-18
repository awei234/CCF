# D02 Team Skill 多 Agent 协作

> 分组：D 实现路线 ｜ 难度 ★★★ ｜ 成本 中 ｜ 推荐度 ★★★
> 状态：备选路线（阶段 3+ 视主线进度启用）｜ 更新日期：2026-08-11

---

## 1. 方向定义

用 **Team Skill（Swarmskill）** 组织多 Agent 分工：leader 拆任务、teammate 分头执行（文献调研 / 实验 / 写作），通过共享文件系统或消息协作，并行推进论文生成。

框架官方支持（Swarmskill 5 文件规范：SKILL.md + roles/ + workflow.md + bind.md + dependencies.yaml；分布式 team 有 leader/teammate 配置）。

## 2. 为什么选

- **并行提升深度**：文献调研和实验可并行，产出质量理论上高于单 Agent 串行
- **官方两条基本思路之一**："通过单个 skill 或 team skill 实现论文自动化生成"
- **天然对齐 FARS 的"科研装配线"模式**（Ideation/Planning/Experiment/Writing 分模块并行）

## 3. 可行性分析

| 项 | 分析 |
|---|---|
| 框架支持 | ✅ Swarmskill 规范 + 分布式 team 配置（`resources/config.team.distributed.*.yaml`）|
| 协作机制 | ✅ 框架 team 目录（`agents/team/`：leader/teammate、a2x 协议）|
| 成本 | ⚠️ 多 Agent 并行 = Token 消耗上升；DeepSeek 下仍可控（单篇目标 $10 量级）|
| 复杂度 | ⚠️ 角色边界、上下文隔离、结果汇总都需要设计，开发量大于 D01 |
| 风险 | ⚠️ FARS 证明"多模块并行"未必赢过"单 Agent 深思"（5.06 vs 5.45）；协作开销可能拖慢迭代 |

## 4. 所需源码改动点

- 新增 team skill（纯资源，放 `03_技术实现/custom_skills/` 或 resources 目录）
- 可选：扩展 teammate 的默认 prompt / 共享工作区约定（轻量源码改动）

## 5. 对应评分维度

实验严谨性（15%）+ 相关工作完整性（10%）——并行调研/实验可提升深度

## 6. 优先级

**中（备选）**。若 阶段 2 后单 Agent + rail 方案已达标，此方向降级；若单 Agent 质量见顶，再启用作提升手段。

## 7. 参考依据

- `docs/zh/SwarmSkills.md`（5 文件规范）
- `resources/config.team.distributed.leader.yaml` / `teammate.yaml`
- FARS 流水线设计（四模块并行）

## 8. 待办清单

- [ ] 阅读 SwarmSkills 规范与 team 配置范例
- [ ] 设计角色：literature_agent / experiment_agent / writing_agent
- [ ] 定义共享工作区约定（results.json 格式先行）
- [ ] （视主线进度）原型验证并行 vs 串行质量差
