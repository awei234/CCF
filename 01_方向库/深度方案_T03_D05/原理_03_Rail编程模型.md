# 原理 03：Rail 编程模型（自定义 rail 开发手册）

> 目标：让你能**直接写出**可运行的科研管控 rail。本文件是 D03（Rail 增强 Harness）的 API 层参考——钩子签名、context 字段、priority 规则、三大操作协议、注册路径、测试范式，全部基于对真实 rail 实现与官方文档的逐行探索。
> 前置：装好环境后先跑通 `docs/zh/Harness.md` §6.1 的最小示例。
> 更新日期：2026-08-11

---

## 1. 最小示例（先跑通这个）

来源：`docs/zh/Harness.md` §6.1（第 553-571 行）

```python
from openjiuwen.harness.rails import DeepAgentRail

class AuditRail(DeepAgentRail):
    priority = 70   # 数值越大越先执行

    async def before_tool_call(self, ctx):
        tool_name = ctx.inputs.tool_name
        tool_args = ctx.inputs.tool_args
        # 你的逻辑...

    async def after_task_iteration(self, ctx):
        ...
```

**要点**：继承 `DeepAgentRail`，定义 `priority`，覆写钩子。就这么简单。

---

## 2. 钩子清单与签名

所有钩子：**`async def hook(self, ctx: AgentCallbackContext) -> None`**——返回 None，一切效果靠**就地修改 ctx**。

| 钩子 | 触发时机 | 典型用途 |
|---|---|---|
| `init(self, agent)` / `uninit(self, agent)` | 注册/注销生命周期（同步）| 抓 agent 引用、注册工具（`agent.ability_manager.add_ability`）、注入系统提示 |
| `before_invoke` / `after_invoke` | 外层 DeepAgent 调用前后 | 写 ctx.extra 频道键（ResponsePromptRail）；结算清理（CodeTaskPlanningRail）|
| `before_task_iteration` / `after_task_iteration` | 外层 Task Loop 轮次 | 改写任务指令、检测完成、todo 同步 |
| `before_model_call` / `after_model_call` | 内层 ReAct 模型调用 | **注入规则段**（main 入口）；切换模型；校验生成内容 |
| `before_tool_call` / `after_tool_call` | 内层 ReAct 工具调用 | **拦截工具**（main 入口）；**改写 tool_result**；todo 计数 |
| `on_model_exception` / `on_tool_exception` | 内层异常 | 上下文修复、异常治理 |
| `get_callbacks(self) -> dict[AgentCallbackEvent, callable]` | 可选覆写 | 替换特定事件处理器（代理/包装 rail 时）|

**对我们的映射**：

| rail | 主钩子 | 为什么 |
|---|---|---|
| F02 实验规划 | `before_tool_call` + `after_tool_call` | 拦截 plan.json 写入 / 校验执行产物 |
| F03 结果一致 | `after_model_call` | 校验模型刚生成的论文文本 |
| F04 引用核验 | `after_model_call` + `after_tool_call` | 校验写作产物里的引用 |
| F01 写作质量 | `before_model_call`（注入规则）+ `after_model_call`（校验）| 规则先注入，再校验产出 |

---

## 3. AgentCallbackContext 字段（你能拿到什么）

| 字段 | 类型 | 用途 |
|---|---|---|
| `ctx.agent` | DeepAgent | 访问 `system_prompt_builder` / `prompt_attachment_manager` / `ability_manager` / `load_state(session)` / `set_llm(model)` / `config.model_name` |
| `ctx.session` | Session | `session.get_session_id()` |
| `ctx.inputs` | ToolCallInputs | `tool_name` / `tool_args`（dict 或 JSON 串）/ `tool_result` / `tool_msg`（ToolMessage，`.content` 可 str 或 block list）/ `tools`（模型可见工具列表，可改写）/ `tool_call` / `query` / `result` |
| `ctx.extra` | dict | **跨 rail 共享通道**（`_skip_tool`、`_plan_rejected`、channel 键等）|
| `ctx.context` | 模型上下文窗口对象 | 装 context mutator、修上下文 |
| `ctx.exception` | Exception | after_tool_call / on_*_exception 时携带 |

> 核心记忆：`ctx.inputs` 管"工具调用与结果"，`ctx.extra` 管"rail 间通信"，`ctx.agent` 管"能力与提示词"。

---

## 4. priority 规则（已确证）

**数值越大，钩子越先执行。**（证据：`tool_restriction_rail.py:78` "priority: int = 100  # High priority to run before other rails"；`skill_retrieval_prompt_rail.py` 用 `SkillUseRail.priority - 1` 表示"在它之后跑"。）

现有值表（避免撞车）：

| priority | rail |
|---|---|
| 5 | RuntimePromptRail / ResponsePromptRail（先铺基础设施 prompt）|
| 75 | MultimodalImageRail |
| 76 | PlanApprovalRail（在 AgentModeRail 85 之后 → 76<85 合理）|
| 78 | PlanApprovalInterruptRail |
| 80 | CodeConfirmInterruptRail |
| 85 | AvatarPromptRail |
| 90 | CodeAgentRail |
| 95 | CircuitBreakerRail / SubagentRail |
| 100 | ToolRestrictionRail（最优先拦截）|
| 默认 | 基类默认（RailManager 扩展默认 50）|

**我们的选择：20–50 区间**——晚于基础设施 rail（5），早于能力 rail（75+），避免与既有值冲突。

---

## 5. 三大操作协议（rail 的"手"）

### 协议 A：拦截工具（deny / skip）

参照 `tool_restriction_rail.py`（`before_tool_call` 内）：

```python
ctx.extra["_skip_tool"] = True                        # 引擎跳过执行该工具
ctx.inputs.tool_result = {"success": False, "error": "禁止：..."}  # 给返回端
ctx.inputs.tool_msg = ToolMessage(content="禁止：...", tool_call_id=...)  # 给模型看的消息
```

引擎看到 `_skip_tool` → 不执行工具 → 把 `tool_msg` 喂回模型 → 模型收到"被拒"信号并修正。

**F02 用法**：检测到 agent 写 `plan.json` 且内容不达标 → 拦截写入，`tool_msg` 返回校验报告引导重写。

### 协议 B：改写 tool_result（篡改 / 追加提示）

参照 `code_plan_approval_rail.py:186-189`（`after_tool_call` 内）：

```python
ctx.inputs.tool_msg.content = str(ctx.inputs.tool_msg.content) + "\n[审批提示] ..."
# 或整体替换：
ctx.inputs.tool_result = new_result
```

**F02 用法**：agent 写 plan.json 后，校验通过时在 tool_result 追加"✓ 计划已通过校验"，让模型知道可以继续。

### 协议 C：注入规则段（before_model_call 内）

参照 `project_memory_rail.py`（每轮重建 system prompt section）：

```python
agent.system_prompt_builder.remove_section("paper_control")
agent.system_prompt_builder.add_section(
    PromptSection(
        name="paper_control",
        content={"cn": "【论文管控规则】\n1. ...", "en": "..."},
        priority=120,   # section 的优先级（与 rail priority 无关）
    )
)
```

**F01/F02 用法**：每轮模型调用前，把当前阶段该遵守的规则注入 system prompt。

### 协议 D：强制结束本轮（可选）

```python
ctx.request_force_finish({"output": "任务中止：...", "result_type": "answer"})
```

### 协议 E：HITL 确认（可选，决赛场景）

继承 `ConfirmInterruptRail`，`self.interrupt(InterruptRequest(...))` 发起用户确认，`self.reject(tool_result={"error": ...})` 拒绝。

---

## 6. 注册路径（三选一）

### 路径 A：Swarm 声明式装配（正式版）

`jiuwenswarm/agents/swarm/providers/code_rails.py` 样式：

```python
from ... import harness_element, ElementKind, ConstructionInput, context_field

class ExperimentPlanningInput(ConstructionInput):
    strict: bool = context_field(attr="experiment_planning.strict", default=True)

@harness_element(
    kind=ElementKind.RAIL,
    name="swarm.experiment_planning_rail",
    description="强制 plan.json 合规",
    input_model=ExperimentPlanningInput,
)
def build_experiment_planning_rail(params, ctx):
    inp = ExperimentPlanningInput.resolve(params, ctx)
    return ExperimentPlanningRail(strict=inp.strict)
```

然后：`registry.py` re-export + `config_specs.py` 对应 role 加 `RailSpec(type=..., params=...)`。

### 路径 B：单 agent 动态挂载（调试）

`interface_deep.py` 的 `_build_*_rail()` 工厂 + `await self._instance.register_rail(rail)` / `unregister_rail(rail)`。

### 路径 C：运行时热加载（开发期首选）

把 rail 放 agent workspace 的 `extensions/<name>/rail.py`（类名 `class XxxRail(DeepAgentRail)`，含 `priority`），通过 `RailManager.hot_reload_rail(name, enabled)` 动态加载/卸载。

> 决策：**开发期用 C（改即生效）→ 稳定后移植 A（正式装配）**。

---

## 7. 测试范式（先写测试再写实现）

参照 `tests/unit_tests/agents/harness/code/test_code_task_planning_rail.py`——**不 mock 框架，直接调钩子**：

```python
import pytest
from openjiuwen.core.single_agent.rail.base import AgentCallbackContext, ToolCallInputs

class FakeAgent:
    def __init__(self):
        self.prompt_attachment_manager = PromptAttachmentManager()
        self.config = SimpleNamespace(model_name="")

def _ctx(agent, tool_name="write_file", tool_args=None):
    return AgentCallbackContext(
        agent=agent,
        session=FakeSession("sess1"),
        inputs=ToolCallInputs(tool_name=tool_name, tool_args=tool_args or {}),
    )

@pytest.mark.asyncio
async def test_plan_rail_rejects_bad_plan():
    rail = ExperimentPlanningRail()
    await rail.before_tool_call(_ctx(rail._agent, "write_file", {"path": "plan.json", "content": "{}"}))
    # 断言：ctx.extra["_skip_tool"] is True
    # 断言：ctx.inputs.tool_msg.content 包含校验报告
```

**关键认知**：钩子签名即测试接口——不需要起 DeepAgent，构造 `AgentCallbackContext` + 薄 Fake 即可逐钩子断言。

---

## 8. 三个参考实现精读（写之前先读这三份）

| 参考 | 文件 | 学什么 |
|---|---|---|
| 拦截协议 | `agents/harness/common/auto_memory/tool_restriction_rail.py` | `_skip_tool` + tool_result + tool_msg 的完整写法；priority=100 最优先 |
| 注入协议 | `agents/harness/common/rails/project_memory_rail.py` | 每轮 before_model_call 重建 section；init/uninit 抓 agent |
| 状态机 | `agents/harness/code/rails/code_plan_approval_rail.py` | after_tool_call 检测特定工具 → 改 tool_msg 追加 marker；agent.load_state/get_plan_file_path |

---

## 9. 常见坑

| 坑 | 说明 |
|---|---|
| priority 撞车 | 先查现有值表，选 20-50 |
| 同 priority 顺序不保证 | 依赖顺序的 rail 用 `X.priority - 1` 显式表达 |
| section 互踩 | 多个 rail 都在 before_model_call 重建 section → 用固定 name + 先 remove 再 add |
| 误伤正常流程 | 校验失败优先"引导修正"（返回报告），不要一律 request_force_finish 硬停 |
| 网络调用拖慢 | F04 的在线核验设计成异步/批处理/单独工具，rail 只做触发与结果消费 |
| 编译态基类 | openjiuwen 安装版为 mypyc 编译态 → 用 `inspect.signature` 核对实际签名（列入待实测清单）|

---

## 10. 待实测验证项

- [ ] `from openjiuwen.harness.rails import DeepAgentRail` 可导入且钩子签名一致
- [ ] `ctx.extra["_skip_tool"]` 拦截协议在安装版生效
- [ ] `PromptSection` 的构造参数（name/content/priority）与本文档一致
- [ ] `ToolMessage` 的构造参数（content/tool_call_id）
- [ ] `system_prompt_builder.add_section/remove_section` 行为与 project_memory_rail 一致
