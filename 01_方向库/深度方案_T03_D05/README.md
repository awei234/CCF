# 深度方案总览：T03 Agent 自演进 × D05 混合架构

> 本目录是「T03（论文主题：Agent 自演进）+ D05（实现路线：混合架构）」两条主线的**深度落地文档**。
> 所有原理均基于对 JiuwenSwarm 源码、openjiuwen 配置与 prompt 的逐层探索（2026-08-11），精确到钩子签名、pipeline 阶段、配置字段与真实代码路径。
> 目标读者：开发执行者本人。请按顺序阅读 3 篇原理，再按 3 篇行动文档执行；动手前对照 §1.5 的 6 篇细化文档拿命令与代码。

---

## 1. 这 7 篇文档解决什么问题

| 文档 | 回答的问题 | 内容粒度 |
|---|---|---|
| `README.md`（本文件）| 为什么是这两条线？怎么用这套文档？| 决策层 |
| `原理_01_D05混合架构.md` | 四层系统怎么搭？数据怎么流动？| 架构层 |
| `原理_02_T03自演进机制.md` | Auto Harness 到底怎么"自演进"？| 机制层 |
| `原理_03_Rail编程模型.md` | 自定义 rail 怎么写？（钩子/priority/协议）| API 层 |
| `行动_分阶段执行计划.md` | 阶段 0–8 每个阶段干什么？验收什么？| 执行层 |
| `行动_Rail实现规格.md` | F01–F04 四个 rail 的钩子级规格与伪代码 | 代码层 |
| `行动_自演进实验设计.md` | E1–E4 实验怎么跑、数据怎么记录 | 实验层 |

**阅读顺序（第一遍·理解）**：原理_01 → 原理_02 → 原理_03 → 行动_分阶段 → 行动_Rail 规格 + 行动_实验设计。

---

## 1.5 细化文档导航（动手时看这套）

> 原理/行动 7 篇是"为什么"与"做什么"；下面 6 篇 `细化_NN_*` 是"**具体怎么做**"——命令、文件全文、代码、模板，照着手册即可执行。
> 新增于 2026-08-12（细化批）。原 7 篇内容不变，本套是配套执行层。

| 细化文档 | 对应原文档 | 补充了什么（手把手粒度） |
|---|---|---|
| `细化_01_阶段执行手册.md` | 行动_分阶段执行计划 | 每阶段 → 任务卡（命令 / 落点 / 验收），本地 Windows 与服务器双轨命令，风险触发后的精确动作 |
| `细化_02_科研Skill全文与工作区契约.md` | 原理_01 §4、§7 | `research-pipeline/SKILL.md` **全文**（四阶段提示词）+ workspace 完整目录树 + 各文件 JSON Schema + 勾稽链规则表 |
| `细化_03_Rail完整代码_F01-F04.md` | 行动_Rail实现规格 | utils + 四个 rail **完整可运行代码** + tools 工具脚本全文 + pytest 单测全文 + 热加载/移植 checklist |
| `细化_04_AutoHarness自演进E2操作手册.md` | 原理_02 + 实验设计 E2 | `auto_harness/config.yaml` 完整内容 + E2 Round 0/1/2 query 模板 + 每轮记录模板 + 归因码处理表 + 失败预案决策树 |
| `细化_05_实验记录与SAR提交流程.md` | 行动_自演进实验设计 | E1 实验组配置与指标计算公式、E3 基线表、E4 成本 CSV 模板、paperreview.ai 提交步骤、A/B 迭代模板 |
| `细化_06_论文写作与提交四件套.md` | 阶段 4/6/7 | ICLR 模板获取/自制、7 段论文大纲、F01 硬指标清单、图表规范、四件套核对流程 |

**动手顺序**：读 `细化_01`（当前在哪一阶段）→ 按阶段打开对应细化章节 → 代码类先看 `细化_03`（rail）或 `细化_02`（skill）→ 实验类看 `细化_05` → 演进实验看 `细化_04` → 收尾看 `细化_06`。

---

## 2. T03 与 D05 的关系（一句话）

> **D05 是"造一台会自动改进自己的科研机器"，T03 是"把机器会自我改进这件事写成论文"。**
> 系统即实验，论文即系统——D05 造出的每一样东西（rail、skill、Auto Harness 进化记录）最终都变成 T03 论文里的实验证据。

- **D05（工程）**：四层架构（底座 → 流程 → 管控 → 演进）如何拼装。
- **T03（叙事）**：论文核心卖点 = "我们的系统能自主评估 → 改进自己的 Harness → 验证效果"，即自演进闭环。
- 二者共用同一个核心机制：**Auto Harness**（原理_02）。

---

## 3. 核心决策记录（为什么这么选）

### 3.1 决策 1：两层 Auto Harness 各派什么用场

Auto Harness 有**两层**（Meta / Expert），各对应一种产出，我们用它的方式完全不同：

| 层 | 优化对象 | 产出 | 我们的用法 | 理由 |
|---|---|---|---|---|
| **Expert（extended_evolve_pipeline）** | 领域扩展包（tools/skills/rails）| **Harness Package → 热加载即用** | **自演进实验主力**：让系统自己评估"科研严谨性扩展包"缺什么 → 自己设计/实现 rail → 热加载 → 重新生成论文验证 SAR 变化 | 快、无重启、不碰核心源码；论文 E2 实验的证据来源 |
| **Meta（meta_evolve_pipeline）** | 通用底座源码（openjiuwen/harness/**）| **git commit → PR** | **合规交付物**：让系统把改进提 PR 给 openJiuwen；同时满足比赛"框架贡献"硬性要求 | PR 即交付物；也是论文"自演进产出开源贡献"的叙事 |

**结论**：Expert 层负责"进化出能力"（快迭代），Meta 层负责"沉淀贡献"（交付物）。两不冲突，先后有序（先 Expert 跑通闭环，再 Meta 提 PR）。

### 3.2 决策 2：自定义 rail 的注册路径（三选一）

源码探索确认了 rail 的**三条注册路径**，选型如下：

| 路径 | 机制 | 适用阶段 | 选型 |
|---|---|---|---|
| A. Swarm 声明式装配 | `@harness_element(kind=ElementKind.RAIL)` + `config_specs.py` 的 `RailSpec` | 正式版、随产品发布 | ✅ **正式版（阶段 2+）** |
| B. 单 agent `register_rail()` | `interface_deep.py` 里 `_build_*_rail()` + 生命周期挂载 | 深度集成、调试 | 备选 |
| C. 运行时热加载 | `extensions/<name>/rail.py` 放工作区 + `RailManager.hot_reload_rail()` | **开发期快速迭代** | ✅ **开发期（阶段 2）** |

**结论**：开发期用 C（改 rail 立即生效、不用重启 agent，和 Auto Harness Expert 层的 Package 机制一致）；稳定后移植到 A 进入正式装配链。

### 3.3 决策 3：priority 值域

源码实证：**priority 数值越大，钩子越先执行**。既有值表（5/75/76/78/80/85/90/95/100）。我们的 rail 选 **20–50 区间**（晚于基础设施 rail 5，早于能力 rail 75+，互不干扰）。

### 3.4 决策 4：与 T04 兜底的关系

- T03（自演进）是**主卖点**，但 E2 实验有不确定性（依赖 Auto Harness 环境稳定性）。
- **兜底路径**：若阶段 5 自演进闭环跑不通（无法产出 E2 数据），论文叙事重心切到 **T04（实验严谨性与反捏造）**——它只需要 F02/F03/F04 三个 rail 的效果数据（确定性产出），"自演进"降级为 Future Work。
- **关键**：F02/F03/F04 是两条路共用的地基，**永远不白做**。

---

## 4. 系统全景（四层架构预览）

```
┌────────────────────────────────────────────────────────────┐
│ 第4层 演进层：Auto Harness（原理_02）                        │
│   Expert: 自评 → 设计 rail → 实现 → 热加载 → 再生成论文验证   │
│   Meta:   改底座 → verify → 提 PR（合规交付物）              │
├────────────────────────────────────────────────────────────┤
│ 第3层 管控层：自定义 rail（原理_03 + 行动_Rail实现规格）      │
│   F02 实验规划 ｜ F03 结果一致 ｜ F04 引用核验 ｜ F01 写作质量  │
├────────────────────────────────────────────────────────────┤
│ 第2层 流程层：科研 skill（选题→调研→方法→实验→写作→分析）    │
├────────────────────────────────────────────────────────────┤
│ 第1层 底座：JiuwenSwarm + DeepSeek（config 配置）           │
└────────────────────────────────────────────────────────────┘
数据契约（层间通信）：plan.json → results.json → paper.tex
```

---

## 5. 一句话行动主线

```
阶段 0 环境 → 阶段 1 skill 闭环 + SAR 基线 → 阶段 2 F02/F03/F04 rail + 第二轮提交
→ 阶段 3 A/B 迭代 + E1 实验 → 阶段 4 F01/F07 写作质量 → 阶段 5 Auto Harness 自演进（E2）+ PR
→ 阶段 6 论文冻结 → 阶段 7 四件套 → 阶段 8 最终提交（10/09）
```

> 详细阶段计划见 `行动_分阶段执行计划.md` 与 `细化_01_阶段执行手册.md`。

---

## 6. 关键事实速查（探索结论，写文档时的锚点）

| 事实 | 结论 | 证据位置 |
|---|---|---|
| Auto Harness 两条 pipeline | `meta_evolve_pipeline`（assess→plan→implement→verify→commit→publish_pr→learnings）与 `extended_evolve_pipeline`（assess→select_pipeline→design_ext→implement_ext→verify_ext→build_verify→merge→activate）| `run_log_status.py`、`orchestrator.py`（openjiuwen）|
| 默认 pipeline | service 主路径默认 `EXTENDED_EVOLVE_PIPELINE`；Scheduler/TUI 默认 `META_EVOLVE_PIPELINE` | service.py、scheduler.py |
| rail 基类 | `from openjiuwen.harness.rails import DeepAgentRail`；钩子全为 `async (ctx)->None`，返回 None，靠改 ctx 生效 | `openjiuwen/harness/rails/base.py` |
| priority 规则 | **数值大先执行**；现有值 5/75/76/78/80/85/90/95/100；我们选 20-50 | `tool_restriction_rail.py:78` 等 |
| Auto Harness 配置位置 | **实测修正**：`~/.jiuwenswarm/auto-harness/config.yaml`（jiuwenswarm `service.py:72,239`，`get_user_workspace_dir()` = `~/.jiuwenswarm`）；openjiuwen 文档假设的 `~/.openjiuwen/auto_harness` 在本仓库不适用（见细化_04 修正记录）| 细化_04 |
| DeepSeek 配置 | `client_provider: OpenAI` + `api_base: https://api.deepseek.com` + `model_name: deepseek-chat`；`timeout > stream_first_chunk_timeout` | `jiuwenswarm/resources/config.yaml` 235-292 行 |
| 源码贡献抓手 | Auto Harness 配置 `extensions.stage_registrars / pipeline_registrars` 是扩展注册点 → 可向 openJiuwen 提 PR | openjiuwen config.yaml |

---

## 7. 待实测验证清单（安装环境后校准）→ 2026-08-12 已实测

> 以下项已于 2026-08-12 在服务器（/home/vergil/CCF/.venv，openjiuwen 0.1.16）实测验证：

- [x] `from openjiuwen.harness.rails import DeepAgentRail` 可导入；钩子签名全部 `(self, ctx: AgentCallbackContext) -> None`（含 before_invoke/before_model_call/before_tool_call/after_tool_call/after_model_call/after_task_iteration/after_invoke/on_model_exception/on_tool_exception/init/uninit）
- [x] **priority 规则实测**：数值大先执行（80→50→30），默认值 50
- [x] `AgentCallbackContext` 字段实测：agent/event/inputs/config/session/context/extra/exception/retry_attempt 等
- [x] `ToolCallInputs` 字段实测：tool_call/tool_name/tool_args/tool_result/tool_msg
- [x] **拦截协议实测**：`ctx.extra["_skip_tool"]=True` + `ctx.inputs.tool_result={...}` 可直接赋值生效
- [x] DeepSeek 配置：`deepseek-v4-flash`（OpenAI 兼容），`jiuwenswarm chat` 实测应答成功
- [ ] `/auto-harness run --pipeline optimize_expert_harness` 完整交互流程（阶段 5 实测）
- [ ] Extended pipeline 产出的 Package 热加载激活（阶段 5 实测）
- [ ] Meta pipeline 提 PR 全链路（阶段 5 实测，需 GitCode token）

**实测差异记录**（与探索时文档的出入）：
1. `AgentCallbackContext.inputs` 类型标注为 `EventInputs`（ToolCallInputs 是其子类）
2. `ToolMessage` 不在 `rail/base` 模块（需从其他模块导入；拦截用 tool_result 即可，引擎消费 `_skip_tool`）
3. 新增钩子 `before_steering_drain`、`on_user_message`（0.1.16 比探索时版本多）
