# D03 Rail 增强 Harness（官方进阶思路）★核心主线

> 分组：D 实现路线 ｜ 难度 ★★★★ ｜ 成本 中 ｜ 推荐度 ★★★★★
> 状态：阶段 2 主开发 ｜ 更新日期：2026-08-11
> **这是整个参赛方案的技术核心，也是论文"方法合理性"维度的直接证据。**

---

## 1. 方向定义

**修改 JiuwenSwarm 源码，通过自定义 rail 拓展 harness 能力**，让 harness 在 Agent 科研全流程的关键节点进行工程化管控（强制规划、校验结果、拦截捏造），而不只是靠模型自觉。

官方进阶思路原文："修改 JiuwenSwarm 源码，通过 rail 拓展 harness 能力，实现更好效果"。

核心哲学：`Agent = Model + Harness`——模型负责推理，Harness 负责纪律。**科研严谨性不该靠模型的运气，要靠 rail 的强制。**

## 2. 为什么选（五重收益）

1. **合规硬性要求**：规则要求"必须修改 JiuwenSwarm 源码"，D03 天然满足
2. **官方背书**：是官方明说的进阶思路，评委理解成本最低
3. **评分维度自洽**：论文方法（20%）写"rail 生命周期改造"；实验（15%）就是 rail 的效果；创新性（25%）对应 FARS 论文 §6 指出的空白——"需要更强的实验规划 scaffold"
4. **差异化**：绝大多数队伍只会堆 prompt，改 rail 是工程深度分水岭
5. **可交付**：rail 代码 = 技术包核心 + PR 内容

## 3. 可行性分析

| 项 | 分析 |
|---|---|
| 框架支持 | ✅ Rail 是 JiuwenSwarm 一等公民：9 个钩子（before_invoke / before_task_iteration / before_model_call / before_tool_call / after_* / on_*_exception），按 priority 排序，可改写 tool_result |
| 实现范式 | ✅ 参照 `jiuwenswarm/agents/harness/code/rails/*.py`（DeepAgentRail 基类、priority、before/after hook）|
| 挂载方式 | ✅ `agents/swarm/providers/builtin_rails.py` / `code_rails.py` 声明式装配；或直接注册进 config |
| 文档 | ✅ `docs/zh/Harness.md`（623 行）rail 全索引 |
| 风险 | ⚠️ rail 写不好会打断 agent 正常流程（过度校验）；需设计"校验失败 → 引导修正"而非"直接终止" |
| 风险 | ⚠️ openjiuwen 是 git 依赖（agent-core），rail 基类在依赖包里，本地开发需装依赖 |

## 4. 所需源码改动点（第一批）

| 改动 | 位置 | 内容 |
|---|---|---|
| 新增 rail | `jiuwenswarm/agents/harness/code/rails/` 或 `common/rails/` | F02 实验严谨性 Rail、F03 结果一致性 Rail、F04 引用校验 Rail |
| 注册 rail | `agents/swarm/providers/*.py` 或 config | 把新 rail 挂进装配链 |
| 定义科研工作区约定 | 新增工具/文档 | plan.json、results.json 的结构化协议 |
| 文档 | `docs/zh/` | 新 rail 的用法文档（PR 需要）|

## 5. 对应评分维度

**方法合理性（20%）+ 实验严谨性（15%）**——双高权重维度，是分数主引擎。

## 6. 优先级

**阶段 2 最高优先级**。阶段 1 的 D01 跑通后立即转入。

## 7. 参考依据

- `docs/zh/Harness.md`（Rail 生命周期、9 钩子）
- `code/rails/code_plan_approval_rail.py`（含状态机范式）
- `common/rails/project_memory_rail.py`（挂载到生命周期的示例）
- FARS 论文 §5.2 三大失败模式 + §6 未来方向

## 8. 待办清单

- [ ] 精读 Harness.md 的 Rail 章节 + 3 个 rail 实现范例
- [ ] 定义科研流水线的 rail 生命周期挂载点（哪个钩子管控哪一步）
- [ ] 实现 F02 实验严谨性 Rail（第一批）
- [ ] 实现 F03 结果一致性 Rail（第一批）
- [ ] 实现 F04 引用校验 Rail（第一批）
- [ ] 挂载进装配链，跑通带 rail 的完整流水线
- [ ] 写 rail 用法文档（PR 材料）
