---
name: research-pipeline
description: "科研论文全流程流水线：选题（ideation）→ 实验规划（plan）→ 实验执行（experiment）→ 论文写作（writing）。当用户说「科研流水线」「写一篇论文」「做研究」「实验规划」「科研」「论文」等时触发。四阶段按顺序执行，每阶段产出固定文件，遵守工作区数据契约（plan.json → results.json → paper.tex 勾稽一致）。"
trigger: 用户提到「科研流水线」「写论文」「做研究」「实验规划」「科研」「写一篇论文」等关键词时加载。
version: 0.1.0
tags: [research, paper, pipeline]
allowed_tools: [bash, read_file, write_file, webSearch]
---

# 科研流水线（Research Pipeline）

> 你是科研助理，按四阶段产出论文。**每个阶段产出物固定**（完整 Schema 见 `references/workspace_schema.md`），
> 阶段间数据靠工作区文件传递，禁止跨阶段口头承诺。
> **写任何产物前，先读 `references/workspace_schema.md`**，按其目录树与 Schema 落盘。
> 工作区根 = `~/.jiuwenswarm/agent/workspace/`，所有产物写到其下的 `workspace/<project_name>/`。

## 执行顺序（必须遵守）

```
阶段1 Ideation   → proposal.md + idea.json + references/
阶段2 Planning   → plan.json
阶段3 Experiment → experiments/<id>/results.json
阶段4 Writing    → paper/paper.tex → PDF
```

每个阶段写完产出物后：**自检勾稽**（规则表见 `references/workspace_schema.md` §勾稽链），自检不过先补，再进下一阶段。

---

## 阶段 1：Ideation 选题

> 输入：用户选题或种子领域。输出：`proposal.md` + `idea.json` + `references/`。
> 完整操作手册见 `prompts/ideation.md`（Schulman 选题法 + novelty 三步验证）。

### 步骤
1. **调研现状（不许跳过）**：搜 arXiv（https）/ OpenAlex / Crossref（Semantic Scholar 限流严重默认不用），从最新论文往前读。
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
   - `idea.json`：Schema 见 `references/workspace_schema.md` §2.2
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
4. **写 `plan.json`**（Schema 见 `references/workspace_schema.md` §2.6，必须通过 F02 校验）。
5. 复现性声明写进 plan（环境/依赖/随机性）。

### 自检清单
- [ ] experiments ≥ 3
- [ ] 每个实验 baselines ≥ 2、seeds ≥ 3、ablation 前置、budget 估算
- [ ] 主实验含 comparison 类型
- [ ] 顶层含 reproducibility

---

## 阶段 3：Experiment 实验执行

> 输入：plan.json。输出：`experiments/<id>/results.json` + 代码 + 日志。
> 完整操作手册见 `prompts/experiment.md`（FARS 实验执行指南）。

### 步骤
1. **资源盘点**：`nvidia-smi` / `nproc` / `free -h`，所有 GPU/CPU 用满；GPU 被他人占用时用空闲的那张（`CUDA_VISIBLE_DEVICES=N` 指定）。
2. **异步启动，不阻塞**：数据准备 → baseline+方法（后台并行启动）→ 消融（后台并行启动）→ 分析/可视化。
   **训练一律 nohup 后台跑，启动后立即返回，不 `wait` 阻塞**；agent 按固定间隔检查进度（见下方「异步训练规范」），等待期间并行做其他工作。
3. **目录纪律**：每个实验一个目录：
   ```
   experiments/<id>/
   ├── run.py            # 实验脚本
   ├── config.json       # 超参/种子/数据源声明
   ├── results.json      # 唯一数据源（F03 只认这个）
   └── logs/             # train.log（stdout）+ run.pid（进程号）+ progress.md（检查记录）
   ```
4. **结果规范**：`results.json` 见 `references/workspace_schema.md` §2.5（metrics 带 mean/std；config 带 seed）。
5. **诚实执行**：跑不了的一步写 `SKIPPED.md` 说明原因，**不许**静默砍实验；
   负结果如实记录（SAR 对负结果友好）。
6. 后台启动示例（立即返回，不等待；服务器 SSH 环境实测可靠版）：
   ```bash
   # 注意：① 用括号子 shell 包裹（避免 & 把整条链后台化）
   #       ② 用 venv python 绝对路径（SSH 非交互 shell 没有 venv 的 PATH）
   #       ③ setsid + </dev/null（让 SSH 会话立即返回，不等待训练）
   cd experiments/exp1
   ( setsid /home/vergil/CCF/.venv/bin/python run.py > logs/train.log 2>&1 < /dev/null & echo $! > logs/run.pid )
   echo "exp1 已后台启动 PID=$(cat logs/run.pid)，预计 ~120 分钟，每 15 分钟检查一次"
   ```

### 异步训练规范（训练期间的核心动作）

**启动**：`( setsid <venv绝对路径>/python run.py > logs/train.log 2>&1 < /dev/null & echo $! > logs/run.pid )`。三要素：**括号子 shell**（防止 `&` 把整条命令链后台化）、**venv 绝对路径**（SSH 非交互 shell 无 venv PATH）、**setsid + stdin 重定向**（SSH 会话立即返回、断连不杀训练）。PID 落盘供后续检查。

**轮询**（每次检查执行）：
```bash
PID=$(cat logs/run.pid)
if ps -p $PID > /dev/null 2>&1; then echo "状态: RUNNING"; else echo "状态: DONE/DEAD"; fi
tail -n 20 logs/train.log          # 最新进度
ls -la results.json 2>/dev/null    # 产物是否生成
```

**判定三态**：
- **完成**：进程退出 且 `results.json` 完整（含 metrics）→ 记入 progress.md，开始下一个实验
- **失败**：进程退出 但无 results.json，或日志有 Traceback → 读日志定位 → 修复后重启（`nohup ... &` 重来）
- **超时**：超过 plan.json 预算估算 ×1.5 仍未完成 → 检查原因（卡住？OOM？）→ 决定继续等 / 修复 / 砍（砍需写 `SKIPPED.md`）

**节奏**：默认每 10-15 分钟检查一次（长训练）/ 2-5 分钟（短任务）；每次检查后在 `logs/progress.md` 记一行（时间 + 状态 + 最新 loss/指标）。**等待期间不空等**：并行准备下一个实验的 run.py、写分析脚本、整理 references、或写论文其他章节。

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

## 维护说明

- 改 SKILL.md 后**不需要重启**：skill 渐进式按需加载（references/ 内容按需读）
- 每次大改后跑一遍阶段 1 验收：触发 → 四阶段 → PDF → SAR
- 本 skill 是 E1/E2 实验的"对照组配置"之一：E1 对照组 = 本 skill 无 rail；实验组 = 本 skill + F02/F03/F04
