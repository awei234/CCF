# D04 Auto Harness 自演进（论文创新性叙事引擎）

> 分组：D 实现路线 ｜ 难度 ★★★★★ ｜ 成本 高 ｜ 推荐度 ★★★★
> 状态：阶段 5 预研/收尾 ｜ 更新日期：2026-08-11
> **注意：D04 的最大价值不在"功能"，在"叙事"——它是论文主题 T03（Agent 自演进）的实验证据来源。**

---

## 1. 方向定义

利用 JiuwenSwarm 自带的 **Auto Harness** 机制（Meta/Expert 双层），让 Agent 分析自身 harness 不足 → 生成改进方案 → 在独立 worktree 实现 → 验证 → 热加载（Expert）或提 PR（Meta），实现"Agent 改进 Agent"的自演进闭环。

两条官方 pipeline：
- **Meta Evolve Pipeline**：基座层优化（调研→评估→计划→worktree 实现→CI 验证→PR），`--pipeline optimize_meta_harness`
- **Expert Evolve Pipeline**：领域扩展包优化（生成 Package→热加载即插即用），`optimize_expert_harness`

## 2. 为什么选

- **官方内置能力**：Auto Harness 是 JiuwenSwarm 独有卖点（`agents/harness/common/auto_harness/service.py` 2600+ 行），用它做论文实验"零框架成本"
- **新颖度天花板**：T03（Agent 自演进）是官方建议主题，也是 FARS 未解决的前沿问题
- **双用途**：Meta pipeline 产生的 PR = 框架贡献交付物 + 论文"自演进"实验数据
- **对应 FARS 局限 2/3**：创新性不足、机制洞察浅——自演进正是针对性回答

## 3. 可行性分析

| 项 | 分析 |
|---|---|
| 框架支持 | ✅ Auto Harness 完整实现（service.py + openjiuwen.rsi.auto_harness）|
| 依赖 | ⚠️ 需要 GitCode 仓库认证（repo_auth/gitcode.py）、worktree 环境、CI |
| 成本 | ⚠️ 每次演进 run 消耗大（调研+实现+验证），DeepSeek 下也要注意预算 |
| 复杂度 | ⚠️ 最复杂的路线：需要理解 orchestrator、pipeline、Package 生命周期 |
| 风险 | ⚠️ 演进闭环跑通需要较稳的环境；失败排查难。作为"加分项"而非"必选项" |

## 4. 所需源码改动点

- 主要**使用** Auto Harness（配置 + 触发），源码改动少
- 若要体现贡献：给 auto_harness 的 issue_fix 或 pipeline 加能力（如科研场景的验证器）→ 可提 PR
- 论文实验：记录"自演进前后 harness 行为对比"数据

## 5. 对应评分维度

**创新性（25%）**——主引擎；方法合理性（20%）的叙事支撑。

## 6. 优先级

**中（叙事优先，功能其次）**。阶段 2 主线 D03 稳定后，阶段 5 用于产出 PR + 实验数据。

## 7. 参考依据

- `docs/zh/AutoHarness.md`（Meta/Expert 双 pipeline）
- `agents/harness/common/auto_harness/service.py`（核心实现）
- 发布版 `_internal/openjiuwen/rsi/auto_harness/prompts/`（10 个 pipeline 技能 prompt）

## 8. 待办清单

- [ ] 读 AutoHarness.md，理解两条 pipeline 触发方式
- [ ] 准备 GitCode 认证 + worktree 环境
- [ ] 跑通一次 Meta Evolve（让它自己改自己的 rail/prompt）
- [ ] 记录前后对比（作为论文 T03 的实验数据）
- [ ] 整理 PR 内容（框架贡献交付物）
