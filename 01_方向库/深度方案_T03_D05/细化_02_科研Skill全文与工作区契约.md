# 细化 02：科研 Skill 全文与工作区契约（阶段 1 手把手）

> 对应：原理_01 §4（流程层）、§7（数据契约）。
> 解决的问题：**SKILL.md 全文长什么样？工作区目录和每个 JSON 文件长什么样？勾稽链怎么保证？**
> 🔧 2026-08-12 源码核查锚点：
> - 内置 skill 在 `jiuwenswarm/resources/agent/workspace/skills/`（20 个）；运行时自定义 skill 根目录 = **`~/.jiuwenswarm/agent/workspace/skills/<name>/`**（docs/zh/技能.md:167-170）
> - frontmatter 字段（docs/zh/技能.md:557-600）：`name`（kebab-case，推荐）/ `description`（推荐）/ `trigger`（可选，如 doc-update 用法）/ `version`/`author`（可选）/ `tags` / `allowed_tools`（可选）
> - 结构：`SKILL.md` 必填 + `references/`（渐进式披露）+ `scripts/`（可执行脚本）
> - 触发：`react.skill_mode: all`（config.yaml:473）下按 description/trigger 匹配加载；框架**没有**科研/论文 skill → 我们的空白机会
> 更新日期：2026-08-12（细化批）

---

## 0. 落点与一次性配置

### 0.1 文件落点

```
03_技术实现/custom_skills/research-pipeline/        # 开发/源文件（进技术包）
├── SKILL.md                                        # ★全文见 §1
├── prompts/
│   ├── ideation.md                                 # §1.3 的四段提示词单独存（SKILL.md 引用）
│   ├── planning.md
│   ├── experiment.md
│   └── writing.md
└── references/                                     # 渐进式披露资料（工作区 Schema 拷贝）
    └── workspace_schema.md                         # §2 内容的一份拷贝（agent 写文件时对照）

运行时挂载（让 agent 能触发它）：
~/.jiuwenswarm/agent/workspace/skills/research-pipeline/   # 软链或复制
```

### 0.2 挂载命令（阶段 1 做一次）

```bash
# 服务器：复制到运行时 skill 根目录
SKILLS=~/.jiuwenswarm/agent/workspace/skills
mkdir -p $SKILLS
cp -r /home/vergil/CCF/03_技术实现/custom_skills/research-pipeline $SKILLS/

# 确认 config 允许全部 skill 触发（config.yaml 的 react 段）
# react.skill_mode: all   ← 保持默认即可；若为白名单模式则把 research-pipeline 加进 skills 列表

# 验证：触发测试（对话里带"科研流水线"关键词）
jiuwenswarm chat "用科研流水线 skill 完成选题：rail 对捏造率的抑制"
# 预期：agent 输出四阶段推进，并产出 proposal.md/idea.json/plan.json 等
```

> ⚠️ SKILL.md 的 `description` 是触发的关键：**必须包含用户会说的高频词**（如"科研流水线/写论文/科研/实验规划"），否则 skill_mode: all 下也可能匹配不到。

---

## 1. `SKILL.md` 全文（可直接复制）

> 内容改编自 FARS 论文附录 B（`02_情报库/FARS标杆分析/fars_paper_text.txt` 657–1758 行）的四段指南：Ideation / Plan / Experiment / Paper-writing。原文是英文操作手册，这里中文改写并强化"与 rails 配合"的约束（rails 是执法者，skill 是手册）。

```markdown
---
name: research-pipeline
description: "科研论文全流程流水线：选题（ideation）→ 实验规划（plan）→ 实验执行（experiment）→ 论文写作（writing）。当用户说「科研流水线」「写一篇论文」「做研究」「实验规划」「科研」「论文」等时触发。四阶段按顺序执行，每阶段产出固定文件，遵守工作区数据契约（plan.json → results.json → paper.tex 勾稽一致）。"
trigger: "科研流水线|写论文|做研究|实验规划|科研|research pipeline"
version: 0.1.0
tags: [research, paper, pipeline]
allowed_tools: [write_file, edit_file, read_file, bash, web_search, python_execute, latex_compile]
---

# 科研流水线（Research Pipeline）

> 你是科研助理，按四阶段产出论文。**每个阶段产出物固定**（见 §6 契约），
> 阶段间数据靠工作区文件传递，禁止跨阶段口头承诺。

## 执行顺序（必须遵守）

```
阶段1 Ideation   → proposal.md + idea.json + references/
阶段2 Planning   → plan.json
阶段3 Experiment → experiments/<id>/results.json
阶段4 Writing    → paper/paper.tex → PDF
```

每个阶段写完产出物后：**自检勾稽**（§6.2），自检不过先补，再进下一阶段。

---

## 阶段 1：Ideation 选题

> 输入：用户选题或种子领域。输出：`proposal.md` + `idea.json` + `references/`。
> 完整操作手册见 `prompts/ideation.md`（Schulman 选题法 + novelty 三步验证）。

### 步骤
1. **调研现状（不许跳过）**：搜 arXiv / Semantic Scholar / Google Scholar，从最新论文往前读。
   - 近 6 个月在做什么 → 近 1-2 年 SOTA → 经典奠基工作
   - 记下：主要方法、基准与指标、已知局限、公开问题
2. **找缺口**：读最近论文的 Limitations / Future Work；找"简单 baseline 仍然很强"的问题
   （说明社区还没啃下来，是机会）。
3. **生成候选假设**：goal-driven（推荐）——"现有方法在 X 情况下失效，怎么修？"
   必须是可证伪的假设（能设计一个会失败的实验）。
4. **novelty 三步验证（关键，别跳）**：
   - 用你方法的关键词搜 arXiv/S2（搜问题而非只搜方法名）
   - 查"最接近的 Related Work"，确认不是已有方法的特例/换皮
   - 查最近 3 个月是否有并发工作
5. **写产出物**（必须全部完成）：
   - `proposal.md`：Introduction（背景/问题/关键洞见/假设）/ Proposed Approach / Related Work / Experiments（planned）/ Success Criteria / References（全部真实可核验）
   - `idea.json`：见 §3 Schema
   - `references/`：每篇文献一个目录，含 `meta/meta_info.txt`（title/authors/venue/year/URL）+ `sections/`（abstract.md、引言、相关工作等摘要）

### 自检清单
- [ ] 一句话能说清 idea（外行能懂）
- [ ] 有能直接测试假设的实验设计
- [ ] 资源够用（数据/算力/时间）
- [ ] 所有引用真实可核验（F04 会查）
- [ ] 不是已存在工作的换皮（novelty 三步已过）

---

## 阶段 2：Planning 实验规划

> 输入：proposal.md + idea.json。输出：`plan.json`（F02 rail 强制校验，不达标会被打回）。
> 完整操作手册见 `prompts/planning.md`（FARS 实验规划指南）。

### 步骤
1. **把假设拆成可测声明**（能失败才有信息量）："我们的方法优于 X"→ 主实验对比；"组件 A 关键"→ 消融。
2. **设计实验清单**：≥3 个实验，必须包含：
   - 主实验（含 **≥2 个公平 baseline**：1 简单 + 1 强/新近）
   - 每个新组件的**前置消融**（跑实验前就规划好，不许看完结果再补）
   - 每个实验 **≥3 个种子**（同一批种子用于所有方法 = 公平对比）
   - 每个实验**独立声明数据集**（禁止一个数据集当多个用）
3. **预算估算**（FARS 公式）：per-run 时长 × 独立实验数 ÷ 并行度 ≤ 时间预算；
   超了就**先**砍（少 seed/小模型/少数据集），别执行中砍。
4. **写 `plan.json`**（Schema 见 §4，必须通过 F02 校验）。
5. 复现性声明写进 plan（环境/依赖/随机性）。

### 自检清单
- [ ] experiments ≥ 3
- [ ] 每个实验 baselines ≥ 2、seeds ≥ 3、ablation 前置、budget 估算
- [ ] **datasets（复数，数组）独立声明**（F02 校验字段名，2026-08-15 统一：非 dataset 单数）
- [ ] 主实验含 comparison 类型
- [ ] 顶层含 reproducibility
- [ ] status 字段（可选）：取值 `planned|partial|completed`；**缺省视为 completed**，F03 对 completed 强制勾稽 results.json；还没跑的实验请显式标 `planned`，跑了一部分标 `partial`（附 status_note 说明已跑/待跑）

---

## 阶段 3：Experiment 实验执行

> 输入：plan.json。输出：`experiments/<id>/results.json` + 代码 + 日志。
> 完整操作手册见 `prompts/experiment.md`（FARS 实验执行指南）。

### 步骤
1. **资源盘点**：`nvidia-smi` / `nproc` / `free -h`，所有 GPU/CPU 用满。
2. **按依赖序跑**：数据准备 → baseline+方法（并行）→ 消融（并行）→ 分析/可视化。
3. **目录纪律**：每个实验一个目录，支持两级结构（F03 递归读取）：
   ```
   experiments/<id>/
   ├── run.py            # 实验脚本
   ├── config.json       # 超参/种子/数据源声明
   ├── results.json      # 唯一数据源（F03 只认这个）
   └── logs/             # stdout/训练日志
   ```
   多 seed 时用 `experiments/<id>/<seed>/results.json`（每 seed 一份，F03 自动合并）。
   ⚠️ 完成实验后把 plan.json 中对应实验 `status` 改为 `completed`，否则 F03 只提示不阻断，勾稽链失效。
4. **结果规范**：`results.json` 见 §5 Schema（metrics 带 mean/std；config 带 seed）。
5. **诚实执行**：跑不了的一步写 `SKIPPED.md` 说明原因，**不许**静默砍实验；
   负结果如实记录（SAR 对负结果友好）。
6. 并行示例：
   ```bash
   CUDA_VISIBLE_DEVICES=0 python experiments/exp1/run.py &
   CUDA_VISIBLE_DEVICES=1 python experiments/exp2/run.py &
   wait
   ```

### 自检清单
- [ ] 每个 plan 声明的实验都有 results.json（F03 勾稽会查）
- [ ] 每步代码/日志/结果齐全（复现审核要查）
- [ ] 种子固定并写入 config.json

---

## 阶段 4：Writing 论文写作

> 输入：results.json（唯一数字来源）。输出：`paper/paper.tex`。
> 完整操作手册见 `prompts/writing.md`（FARS 论文写作指南）。

### 步骤（写作顺序 ≠ 成稿顺序）
1. 先写 **Method → Experiments → Contributions → Conclusion**
2. 再写 **Introduction**（现在知道要引什么了）
3. 再写 **Related Work**
4. **Abstract 最后写**（150-250 词单段：context → problem → method → key result → implication）

### 成稿结构（F01 硬校验，7 段缺一不可）
```
1. Title
2. Abstract
3. Introduction（含 itemize 贡献列表 + 路线图）
4. Related Work（漏斗：宽→窄→定位收尾 "Unlike ..., our approach ..."）
5. Method（可复现：符号定义 + 算法 + 概览图）
6. Experiments（Setup → Main results → Ablations → Analysis）
7. Discussion / Limitations（诚实局限，负结果加分）
8. Conclusion（不引入新结果）
9. References（15-30 条，全部真实可核验）
```

### 硬规则（rail 会查，别踩）
- **每个数字必须与 results.json 逐字一致**；禁止捏造、禁止外推（F03）
- 表：booktabs 三线表、caption 在表上方、最优值 `\textbf{}` + `\uparrow/\downarrow`、正文 `Table~\ref{}` 引用
- 图：PDF/矢量、字号≥8pt、caption 在下方、正文 `Figure~\ref{}` 引用、全套统一配色
- 引用：只用 `references/` 里真实文献；`\citep{}` 括号式、`\citet{}` 文本式
- 词数 ≥4000、图 ≥4、表 ≥6、必须含复杂度分析（O(·)）（F01）

### 自检清单
- [ ] 7 段结构齐全
- [ ] 数字全部有 results.json 出处
- [ ] 引用全部在 references/ 池中（或已在线核验）
- [ ] 词数/图表/复杂度达标

---

## 附录：数据契约速查（阶段间传递）

```
proposal.md ─→ idea.json ─→ plan.json ─→ experiments/*/results.json ─→ paper/paper.tex
   (F05/F02 校验)   (F02 强制)     (F03 勾稽)          (F03/F04/F01 校验)
```

| 文件 | 阶段 | 校验者 |
|---|---|---|
| proposal.md | 1 | 人工/F05（novelty 声明）|
| idea.json | 1 | 人工/F05 |
| references/ | 1 | F04（引用候选池）|
| plan.json | 2 | **F02**（不达标打回）|
| experiments/*/results.json | 3 | **F03**（勾稽：plan 声明的实验都跑了吗）|
| paper/paper.tex | 4 | **F03**（数字有出处）+ **F04**（引用可查）+ **F01**（硬指标）|

---

## 维护说明

- 改 SKILL.md 后**不需要重启**：skill 渐进式按需加载（references/ 内容按需读）
- 每次大改后跑一遍 阶段 1 验收：触发 → 四阶段 → PDF → SAR
- 本 skill 是 E1/E2 实验的"对照组配置"之一：E1 对照组 = 本 skill 无 rail；实验组 = 本 skill + F02/F03/F04

---

## 2. 工作区完整目录树（数据契约实体）

> 每个论文项目一个工作区目录。skill 在 `workspace/` 下按此结构产出；rails 按此结构校验。

```
workspace/<project_name>/
├── proposal.md                     # 阶段1：研究提案（§2.1）
├── idea.json                       # 阶段1：结构化选题（§2.2）
├── references/                     # 阶段1：文献池（§2.3）
│   ├── references_index.json       # 可选项：{bibkey: {title, year, ...}}（F04 优先读）
│   ├── smith2023/                  # 每文献一个目录，目录名 = bibkey
│   │   ├── meta/
│   │   │   ├── meta_info.txt       # title / authors / venue / year / URL
│   │   │   └── bibtex.txt          # BibTeX 条目
│   │   └── sections/
│   │       ├── abstract.md
│   │       ├── 1 Introduction.md
│   │       └── 2 Related Work.md
│   └── jones2024/ ...
├── plan.json                       # 阶段2：实验计划（F02 强制校验）
├── experiments/                    # 阶段3：实验产物区
│   ├── exp1/
│   │   ├── run.py                  # 实验脚本
│   │   ├── config.json             # 超参/种子/数据源（§2.4）
│   │   ├── results.json            # 唯一数据源（§2.5，F03 只认这个）
│   │   └── logs/                   # stdout/训练日志
│   ├── exp2/ ...
│   └── shared/                     # 共享工具（data_loader/metrics/models/utils）
└── paper/
    ├── paper.tex                   # 阶段4：论文（F01/F03/F04 校验）
    └── figures/                    # 图表（数据来源可追溯）
        ├── fig1_arch.pdf
        └── ...
```

### 2.1 `proposal.md` 结构（必含小节）

```
# <论文标题>（研究提案）
## Introduction      # 背景 / 问题陈述 / 关键洞见 / 假设
## Proposed Approach # 概述 / 方法细节 / 关键创新
## Related Work      # 关键文献 / 与我们的差异 / 定位
## Experiments       # 计划实验 / 基准 / 指标 / 预期结果
## Success Criteria  # 什么结果证实/证伪假设
## References        # 完整引用列表（必须全部真实可核验）
```

### 2.2 `idea.json` Schema

```json
{
  "title": "论文标题",
  "description": "1-3 句话：提出什么",
  "motivation": "为什么重要、填什么缺口",
  "proposed_approach": "高层方法 + 为什么有效",
  "related_work": ["真实文献：作者/标题/年份", "与我们的差异"],
  "hypothesis": "可证伪假设",
  "success_criteria": "证实/证伪的判据",
  "topic_mapping": "context | memory | self-evolution"
}
```

### 2.3 `references/` 规范

- 每文献一个目录，**目录名 = BibTeX key**（F04 池匹配用）
- `meta/meta_info.txt` 固定四行头：`title:` / `authors:` / `venue:` / `year:` / `url:`
- `meta/bibtex.txt`：完整 BibTeX 条目（写作阶段直接引用）
- 可选 `references_index.json`：`{"smith2023": {"title": "...", "year": 2023}, ...}`
- **所有文献必须是真实可核验的**（novelty 三步里搜到的，F04 会查）

### 2.4 `experiments/<id>/config.json` Schema

```json
{
  "experiment_id": "exp1",
  "seed": 42,
  "dataset": "数据集名（与 plan.json 声明一致）",
  "model": "deepseek-v4-flash",
  "hyperparams": {"lr": 0.001, "epochs": 50},
  "baseline_of": null,
  "created_at": "2026-08-24T10:00:00+08:00"
}
```

### 2.5 `experiments/<id>/results.json` Schema（F03 唯一数据源）

```json
{
  "experiment": "exp1",
  "metrics": {
    "acc": {"mean": 87.3, "std": 0.2},
    "latency_ms": {"mean": 12.3, "std": 0.5}
  },
  "config": {"lr": 0.001, "epochs": 50, "seed": 42},
  "runtime_minutes": 45,
  "notes": ""
}
```

> 论文里出现的任何数字，要么等于这里某个值，要么能由这里推导（均值/百分比）——F03 就这么验。

---

## 3. 勾稽链规则表（rails 校验"计划-执行-报告"一致）

| # | 勾稽规则 | 检查方 | 不满足时 |
|---|---|---|---|
| 1 | plan.json 声明且状态为 **completed/缺省** 的每个 experiment id，在 `experiments/<id>/results.json` 存在（planned/partial 仅提示不阻断） | F03 `_plan_results_missing` | 引导：补跑实验 或 从论文删除相关论断 |
| 2 | paper.tex 每个数字在 results.json 有出处（精确或推导）| F03 `_match` | 注入"未验证数字"清单引导修正 |
| 3 | paper.tex 每个 `\cite{key}` 在 references/ 池命中 | F04 | 引导替换为池中文献 或 在线核验 |
| 4 | plan.json 中 baseline/ablation 声明在论文 Experiments 中体现 | 人工/赛后复现审核 | 阶段 3 的 E1 指标"匹配率"统计用 |
| 5 | 论文图表数据源自 results.json | F07 生成规范 + F03 | 图表脚本数据源只允许 results.json |

---

## 4. 阶段 1 验收清单（本阶段用）

- [x] `SKILL.md` 挂载到 `~/.jiuwenswarm/agent/workspace/skills/research-pipeline/`（✅ 2026-08-14）
- [x] 触发测试成功（✅ 2026-08-14：`jiuwenswarm chat` 识别触发词并完整跑完 Ideation，产出 proposal.md + idea.json + references/ 17 篇；Planning 阶段待任务 3 继续）
- [x] 工作区产物齐全：proposal.md + idea.json + references/ + plan.json + experiments/*/results.json + paper.tex（✅ 2026-08-14，rail-fabrication-context 工作区）
- [x] paper.tex 编译出 PDF（✅ 2026-08-14，texlive 2026 装于服务器 /data，minimal_iclr 模板，0 错误）
- [x] SAR 基线分记录在案（✅ 2026-08-14：v1 基线 5.8 分，见 05_评测与迭代/基线分.md）

> 下一步：阶段 2 实现 F02/F03/F04 rail（细化_03），挂载后这三件产物开始被强制校验。
