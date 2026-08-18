# 行动：Rail 实现规格（F01–F04 钩子级规格 + 伪代码）

> 目标：四个科研管控 rail 的**可直接编码的规格**——挂载点、校验逻辑、数据协议、修正引导、伪代码。
> 所有 API 基于 原理_03（DeepAgentRail / AgentCallbackContext / 三大协议）。
> ⚠️ 伪代码为设计稿，实际以安装后的 openjiuwen 版本为准（见各节"待实测"）。
> 更新日期：2026-08-11

---

## 0. 公共约定

### 0.1 文件位置（开发期）

```
03_技术实现/custom_rails/           # 开发期（热加载测试）
├── experiment_planning_rail.py     # F02
├── result_consistency_rail.py      # F03
├── citation_verification_rail.py   # F04
└── writing_quality_rail.py         # F01
03_技术实现/tools/
├── paper_metrics.py                # F01 配套：LaTeX 指标解析
├── citation_checker.py             # F04 配套：arXiv/S2 核验
├── figure_generator.py             # F07 配套：图表生成
└── resource_logger.py              # F06 配套：资源打点
```

### 0.2 priority 分配（20–50 区间，互不冲突）

| rail | priority | 说明 |
|---|---|---|
| F02 实验规划 | 50 | 最早：规划阶段就要管住 |
| F03 结果一致 | 45 | 写作阶段 |
| F04 引用核验 | 40 | 写作阶段（网络调用，别阻塞太久）|
| F01 写作质量 | 35 | 最后一道综合检查 |

### 0.3 产物协议（所有 rail 共享，见 原理_01 §7）

```
workspace/
├── plan.json          # F02 校验对象
├── experiments/*/results.json   # F03 数据源
├── references/        # F04 引用候选池
└── paper/paper.tex    # F03/F04/F01 校验对象
```

---

## 1. 公共工具：JSON 加载与报告（每个 rail 都用）

```python
# utils.py（custom_rails/ 下）
import json, re, pathlib

def load_json(path) -> dict | None:
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None

def build_fix_report(issues: list[str]) -> str:
    """生成给模型看的修正引导消息（中文）"""
    return ("【校验未通过】请修正以下问题后重试：\n" +
            "\n".join(f"- {i}" for i in issues) +
            "\n修正后重新写入，不得绕过校验。")
```

---

## 2. F02 实验规划 Rail（priority=50）

### 2.1 职责

**规划阶段**强制 plan.json 合规，从源头防"实验支撑不足（49.6%）+ 计划执行不匹配（23.9%）"。

### 2.2 plan.json Schema（FARS 附录 B Plan 指南改编）

```jsonc
{
  "project": "论文题目",
  "topic": "官方主题映射（context|memory|self-evolution）",
  "experiments": [
    {
      "id": "exp1",
      "type": "main|ablation|baseline|comparison|analysis",
      "hypothesis": "假设描述",
      "method": "方法",
      "datasets": ["真实数据集名"],        // 禁止单数据集当多个用
      "baselines": ["基线A", "基线B"],     // ★≥2 个公平 baseline
      "seeds": [42, 2024, 2026],          // ★≥3 个种子
      "ablation": "前置规划：消融哪些组件、怎么消融",  // ★必须写进 plan
      "budget": {"tokens_est": 50000, "time_min": 30},  // ★预算估算
      "metrics": ["acc", "cost", ...],
      "expected_output": "results.json 的键名约定"
    }
  ],
  "reproducibility": "环境/依赖/随机性声明"
}
```

### 2.3 校验规则

| 规则 | 失败动作 |
|---|---|
| `experiments` 数量 ≥ 3 | 引导补全 |
| 每实验 `baselines` ≥ 2 | 引导补充（提示"新 baseline 优先"）|
| 每实验 `ablation` 非空（ablation 必须前置规划）| 引导补消融设计 |
| 每实验 `seeds` ≥ 3 | 引导声明种子策略 |
| `datasets` 每实验独立声明 | 引导修正（防单数据集当多个用）|
| 每实验 `budget` 有估算 | 引导按 FARS 公式估算 |
| 主实验必须声明 `comparison` 类型实验（新 baseline 对比）| 引导补充 |

### 2.4 挂载与伪代码

```python
class ExperimentPlanningRail(DeepAgentRail):
    priority = 50

    async def before_tool_call(self, ctx):
        # 拦截：写 plan.json 时先校验内容（协议 A）
        if ctx.inputs.tool_name in ("write_file", "edit_file") and "plan.json" in str(ctx.inputs.tool_args.get("path", "")):
            content = ctx.inputs.tool_args.get("content") or ""
            plan = json.loads(content) if content.strip().startswith(("{", "[")) else None
            issues = self._validate(plan)
            if issues:
                ctx.extra["_skip_tool"] = True
                ctx.inputs.tool_result = {"success": False, "error": "plan.json 校验失败"}
                ctx.inputs.tool_msg = ToolMessage(content=build_fix_report(issues), tool_call_id=ctx.inputs.tool_call.id)

    async def after_tool_call(self, ctx):
        # 跟踪：记录 plan.json 已通过 → 供 F03 做勾稽
        if "plan.json" in str(getattr(ctx.inputs, "tool_name", "")):
            ctx.extra["_plan_valid"] = True

    def _validate(self, plan: dict | None) -> list[str]:
        issues = []
        if not plan: return ["plan.json 不是合法 JSON"]
        exps = plan.get("experiments", [])
        if len(exps) < 3: issues.append(f"experiments 数量 {len(exps)} < 3")
        for e in exps:
            if len(e.get("baselines", [])) < 2: issues.append(f"{e.get('id')}: baselines < 2（公平基线要求）")
            if not e.get("ablation"): issues.append(f"{e.get('id')}: 缺少 ablation 前置规划")
            if len(e.get("seeds", [])) < 3: issues.append(f"{e.get('id')}: seeds < 3")
            if not e.get("budget"): issues.append(f"{e.get('id')}: 缺少预算估算")
        if not plan.get("reproducibility"): issues.append("缺少复现性声明")
        return issues
```

### 2.5 待实测

- `ctx.inputs.tool_call.id` 是否存在（或改用 ctx.inputs.tool_msg 构造）
- write/edit 工具的 tool_args 内容字段名（path/content 或 file_path/file_content）

---

## 3. F03 结果一致性 Rail（priority=45）

### 3.1 职责

**写作阶段**强制论文每个数字能在 results.json 中找到出处，防"捏造结果（最高 77%）"。

### 3.2 校验机制

```
paper.tex 文本 → 提取数值论断（正则）→ 与 experiments/*/results.json 树匹配
两种匹配：
  ① 精确匹配：数字直接等于 results.json 某值
  ② 推导匹配：数字可由 results.json 原始值算出（均值/方差/百分比）
匹配失败 → 列入"未验证数字清单" → 修正引导
```

### 3.3 伪代码

```python
NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?%?")  # 简单版，含单位/百分比

class ResultConsistencyRail(DeepAgentRail):
    priority = 45

    async def after_model_call(self, ctx):
        # 写作阶段：校验模型刚生成的文本
        text = ctx.output if isinstance(ctx.output, str) else str(ctx.output)
        if "paper" not in ctx.extra.get("_stage", ""):
            return  # 非写作阶段跳过（用 ctx.extra["_stage"] 标记阶段）

        results = self._load_all_results(ctx)   # 递归收集 results.json 的值
        unverified = []
        for token in self._extract_numeric_claims(text):
            if not self._match(token, results):
                unverified.append(token)

        if unverified:
            ctx.extra["_unverified_numbers"] = unverified
            # 引导修正（不硬停）：把清单注入系统提示，让 agent 下一轮修正
            agent.system_prompt_builder.remove_section("result_check")
            agent.system_prompt_builder.add_section(PromptSection(
                name="result_check",
                content={"cn": "以下数字在 results.json 中无出处，请核实并修正：\n" + "\n".join(unverified[:20])},
                priority=120,
            ))

    def _load_all_results(self, ctx) -> dict:
        # 遍历 workspace/experiments/*/results.json，拍平为 {键: 值} 字典
        ...

    def _match(self, token, results) -> bool:
        # ① 精确匹配：token 数值 ∈ results 所有数值
        # ② 推导匹配：token 可被 results 中某组值计算得到（均值/百分比）
        # ③ 白名单：章节号/引用编号/日期等非实验数字
        ...
```

### 3.4 数字提取注意

- 排除干扰：章节号（§3.2）、公式编号、（1）、引用 [12]、年份、页数
- 百分比：`23.5\%` 需剥离 LaTeX 转义
- 数量级：确认是否允许"约/约等于"（保守策略：不允许未标注的近似）

### 3.5 与 F02 联动

- `ctx.extra["_plan_valid"]` 为 True 时，校验"plan 声明的实验都有 results.json"（勾稽）
- 缺失实验 → 引导补跑或从论文删除相关论断

### 3.6 待实测

- `ctx.output` 在 after_model_call 的可用性（或需从 ctx.inputs.tool_result 取写作工具结果）
- PromptSection 内容格式（str vs dict）

---

## 4. F04 引用核验 Rail（priority=40）

### 4.1 职责

写作阶段核验每篇引用真实存在，防"假引用（最高 72%）"。

### 4.2 双通道设计

| 通道 | 覆盖 | 限流 |
|---|---|---|
| arXiv API | arXiv 论文 | 免费、宽松（`http://export.arxiv.org/api/query?id_list=...`）|
| Semantic Scholar API | 通用论文 | 免费额度有限 |

**架构**：核验放 `tools/citation_checker.py`（独立可跑）；rail 只做"触发 + 消费结果 + 引导"，避免阻塞。

### 4.3 校验流程

```
paper.tex → 提取 \cite{...} / \bibitem → 引用列表
→ ① 与 references/ 候选池比对（调研阶段已建池）
→ ② 未在池中的走 citation_checker 在线核验（标题/作者/年份模糊匹配）
→ ③ 输出：verified / not_found / ambiguous
失败/模糊 → 引导：替换为池中真实文献，或补调研
```

### 4.4 伪代码

```python
class CitationVerificationRail(DeepAgentRail):
    priority = 40

    async def after_model_call(self, ctx):
        text = ctx.output if isinstance(ctx.output, str) else str(ctx.output)
        if "paper" not in ctx.extra.get("_stage", ""):
            return

        cites = extract_citations(text)          # 正则 \cite{...} 去重
        pool = load_reference_pool(ctx)          # references/ 目录
        bad = [c for c in cites if not self._verify(c, pool)]

        if bad:
            agent.system_prompt_builder.remove_section("citation_check")
            agent.system_prompt_builder.add_section(PromptSection(
                name="citation_check",
                content={"cn": "以下引用未通过核验，请替换为 references/ 中的真实文献：\n" + "\n".join(bad)},
                priority=120,
            ))

    def _verify(self, cite_key, pool) -> bool:
        if cite_key in pool:                     # 候选池命中 → 通过
            return True
        return citation_checker.verify(cite_key) # 在线核验（容错：网络失败不误杀，标 ambiguous）
```

### 4.5 容错规则

| 情况 | 处理 |
|---|---|
| 网络失败 | 不判假引用（标 ambiguous，跳过），避免误伤 |
| 模糊匹配 | 标 ambiguous → 引导人工/agent 确认 |
| 池中命中 | 直接通过（调研阶段已核验）|

### 4.6 待实测

- `\cite` 提取正则对 bibtex/biblatex 两种格式的覆盖
- Semantic Scholar API 免费额度（rate limit 实测）

---

## 5. F01 写作质量 Rail（priority=35）

### 5.1 职责

写作阶段对论文做**硬指标校验**（SAR 高分画像：词数/图表/复杂度/结构），保 SAR 下限。

### 5.2 指标清单

| 指标 | 阈值 | 检查方式 |
|---|---|---|
| 词数 | ≥ 4000 | `tools/paper_metrics.py`（LaTeX 去命令统计）|
| 图数量 | ≥ 4 | `\includegraphics` 计数 + figures/ 文件核对 |
| 表数量 | ≥ 6 | `\begin{table}` 计数 |
| 复杂度分析 | 必须含 | 检测 `complexity`/`复杂度`/`O(` 章节 |
| 结构完整 | 7 段 | Abstract/Intro/Method/Experiments/Discussion/Conclusion/Related Work 章节标题 |
| 负结果 | 建议含 | `\subsection{...Negative...}` 或类似（加分项，非强制）|

### 5.3 伪代码

```python
class WritingQualityRail(DeepAgentRail):
    priority = 35

    async def before_model_call(self, ctx):
        # 规则先注入（协议 C）：告诉 agent 写作硬指标
        agent.system_prompt_builder.remove_section("paper_quality_rules")
        agent.system_prompt_builder.add_section(PromptSection(
            name="paper_quality_rules",
            content={"cn": "【写作硬指标】词数≥4000；图≥4；表≥6；必须含复杂度分析；"
                           "结构：Abstract/Intro/Method/Experiments/Discussion/Conclusion/Related Work；"
                           "负结果诚实报告（加分）。"},
            priority=120,
        ))

    async def after_model_call(self, ctx):
        text = ctx.output if isinstance(ctx.output, str) else str(ctx.output)
        if "paper" not in ctx.extra.get("_stage", ""):
            return
        report = paper_metrics.check(text)      # 工具返回各指标达标情况
        fails = report.fails()
        if fails:
            # 引导补齐（不改内容，只提示缺口）
            agent.system_prompt_builder.add_section(PromptSection(
                name="paper_quality_gaps",
                content={"cn": "当前论文缺口：\n" + "\n".join(fails)},
                priority=130,
            ))
```

### 5.4 paper_metrics.py 要点

- 词数：去 `\...{}` 命令、注释、参考文献区后 split
- 图表：`\includegraphics` / `\begin{table}` 计数
- 复杂度：关键词检测 `O(1)`、`time complexity`、`复杂度`、`Flops` 等
- 输出：`Report(fields: dict[str, (current, threshold, pass)])`

### 5.5 待实测

- after_model_call 拿到的是单轮输出还是全文（可能需要聚合状态）
- PromptSection 多段叠加行为（quality_rules + gaps 并存）

---

## 6. 测试清单（每个 rail）

参照 原理_03 §7 的测试范式（构造 AgentCallbackContext 直接调钩子）：

| rail | 用例 |
|---|---|
| F02 | ① 缺 baseline 被拦 ② 合法 plan 放行 ③ 非法 JSON 被拦 ④ 修正后重写放行 |
| F03 | ① 伪造数字被标记 ② 合法数字放行 ③ 章节号不误伤 ④ plan-产物勾稽缺失被报 |
| F04 | ① 池中引用通过 ② 未知引用走在线核验 ③ 网络失败容错 ④ 假引用被引导 |
| F01 | ① 短文被拦 ② 缺图被拦 ③ 缺复杂度被拦 ④ 全达标放行 |

---

## 7. 联调顺序

1. 单测通过 → 2. 热加载（路径 C）挂到科研 skill 流水线 → 3. 跑一篇论文看 rail 日志（是否误拦/漏拦）→ 4. 调阈值 → 5. 稳定后移植 swarm providers（路径 A）
