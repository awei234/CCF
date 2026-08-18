# F02 实验严谨性 Rail（第一批核心）★

> 分组：F 功能模块 ｜ 实现成本 中 ｜ 影响维度：实验严谨性 15% + 决赛复现安全
> 状态：阶段 2 开发 ｜ 更新日期：2026-08-11

---

## 1. 模块定义

一个自定义 rail，在科研流水线的**规划阶段**强制 Agent 产出合规的 `plan.json`，从源头杜绝"实验支撑不足"（49.6% 中招率）与"计划执行不匹配"（23.9% 中招率）。

**一句话**：不让 Agent"想怎么做就怎么做"，必须先按规格交实验计划，不达标不放行。

## 2. 为什么是第一批

- FARS 评测论文（§5.2）实测：underpowered 实验 49.6%、plan/execution mismatch 23.9%——两大高频失败模式
- 规划合规是最上游的杠杆：plan 对了，下游执行/写作才可能对
- 实现可控：不依赖外部服务，纯 rail 逻辑

## 3. 功能规格

### 3.1 plan.json 强制字段（rail 校验规则）

| 字段 | 规则 | 校验失败处理 |
|---|---|---|
| `experiments[]` | 至少 3 个实验 | 引导补全 |
| 每实验 `baselines` | **≥2 个公平 baseline**（含新 baseline）| 要求补充并说明公平性 |
| `ablation` | 必须前置规划（写在 plan 里，不是事后补）| 要求补 ablation 设计 |
| `seeds` | 多 seed（≥3）固定声明 | 要求声明随机种子策略 |
| `datasets` | 单数据集不得当多个用（每个实验独立声明数据源）| 要求修正 |
| `budget` | 运行时预算估算公式（Token/时长）| 要求按 FARS 附录 B 公式估算 |
| `reproducibility` | 环境/依赖/随机性声明 | 要求补全 |

### 3.2 rail 挂载点

- 钩子：`before_model_call` 或 `before_tool_call`（在写作/执行实验前拦截）
- 或：`after_tool_call` 检查 plan.json 写入动作后的内容
- 失败动作：**引导修正**（返回校验报告让 agent 重写），而非硬终止

### 3.3 与 F03 联动

- plan.json 中声明的每个实验，必须在实验产物目录中找到对应 results.json（F03 执行期校验）
- 形成一个"计划-执行-报告"的勾稽闭环

## 4. 实现要点（参照框架 rail 范式）

```python
# 参照范式：code/rails/code_plan_approval_rail.py / common/rails/project_memory_rail.py
class ExperimentPlanningRail(DeepAgentRailBase):  # 或合适的基类
    priority = 900  # 高优先级，早于其他 rail
    def before_tool_call(self, ctx): ...   # 拦截 plan.json 写入，校验字段
    def after_tool_call(self, ctx): ...    # 校验执行产物与 plan 的勾稽
```

## 5. 挂载方式

- 放 `03_技术实现/jiuwenswarm/jiuwenswarm/agents/harness/code/rails/experiment_planning_rail.py`
- 在 `agents/swarm/providers/*.py` 或 config 中注册

## 6. 验收标准

- [ ] plan.json 缺 baseline 时 rail 能拦截并给出修正指引
- [ ] 合法 plan 不被误拦
- [ ] 论文实验章节的实验数/baseline 数 ≥ plan 声明（F03 联动）

## 7. 参考依据

- FARS 附录 B Plan 指南（plan.json 7 类实验类型表、公平 baseline 规则、预算公式、Plan Quality Checklist）
- `docs/zh/Harness.md` Rail 章节
- `code/rails/code_plan_approval_rail.py`（状态机范式）

## 8. 待办清单

- [ ] 定义 plan.json schema（JSON Schema）
- [ ] 实现字段校验逻辑
- [ ] 实现引导修正消息模板
- [ ] 单测（合法/非法 plan 各若干）
- [ ] 挂载进装配链
