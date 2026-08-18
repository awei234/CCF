# 细化 05：实验记录与 SAR 提交流程（E1/E3/E4 手把手）

> 对应：行动_自演进实验设计（E1/E3/E4）+ 各阶段详细执行手册 阶段 3。
> 解决的问题：**E1 实验到底怎么跑？指标公式怎么算？SAR 怎么提交？A/B 迭代怎么转？数据怎么留痕？**
> 前置：阶段 2 已实现 F02/F03/F04 并热加载生效（细化_03）；本文件全程依赖资源日志（07_记录/）。
> 更新日期：2026-08-12（细化批）

---

## 0. 数据留痕总原则（比赛"可追溯"硬要求）

1. 每个实验在 `05_评测与迭代/` 建独立子目录：`E1_严谨性/`、`E3_基线/`、`E4_成本/`、`自演进实验/`、`提交记录/`
2. **每次运行留四样**：config（模型/rail/skill 版本 hash）、results.json、SAR 记录、资源日志条目
3. 论文写作时所有数字必须来自这些记录（F03 自举校验）
4. CSV 统一格式：`实验ID, 配置hash, 指标, 值, 时间戳`
5. 配置 hash 计算命令（每次运行前后都跑）：

```bash
# 服务器：生成当前配置指纹（rail+skill+模型），存进 CSV
cd /home/vergil/CCF
sha256sum 03_技术实现/custom_rails/utils.py 03_技术实现/custom_rails/*_rail/rail.py \
          03_技术实现/custom_skills/research-pipeline/SKILL.md 2>/dev/null | sha256sum
# 输出一行 hash → 记为该次运行的 config_hash
```

---

## 1. E1 严谨性增益实验（阶段 3 跑，最稳的论文证据）

### 1.1 组别配置

| 组 | 配置 | 样本量 | 主题池 | 模型 | seed 策略 |
|---|---|---|---|---|---|
| 对照组 | 科研 skill **无 rail** | 5 篇 | 固定 5 个选题（见下）| deepseek-v4-flash | 每篇固定 seed=42 |
| 实验组 | 科研 skill **+ F02/F03/F04** | 5 篇 | 同上 5 个选题 | deepseek-v4-flash | 每篇固定 seed=42 |

**变量控制**：唯一变量 = rail。同一 skill 提示词、同一模型、同一选题、同一 seed。
**选题池**（5 个，与主线一致的子问题）：
1. rail 对结果捏造率的抑制效果
2. 实验规划强制（baselines≥2）对论文支撑度的影响
3. 引用核验对假引用率的抑制
4. 数字一致性校验对结果可信度的影响
5. 组合 rail 对 SAR 总分的综合影响

> ⚠️ 选题 1–5 是"我们自己系统的评测论文"，不要和"主线论文"混淆。它们是 E1 的样本。

### 1.2 跑法（每篇论文的固定流程）

```bash
# 对照组（无 rail）：先卸载 rail 再生成
# 触发方式：CLI 对话（Quickstart 确认的入口）或 Web「工作」页输入选题
#   react.skill_mode: all 下，skill 按描述自动触发（细化_02 §1 的 description 写法很关键）
jiuwenswarm chat "用科研流水线 skill 完成以下选题并输出论文：<选题1>"
# → workspace 产出 paper.tex → 编译 PDF → 提交 SAR

# 实验组（有 rail）：确认 rail 已热加载（细化_03 §8.3 的 verify 命令输出 4 行 enabled）
jiuwenswarm chat "用科研流水线 skill 完成以下选题并输出论文：<选题1>"
```

每组每篇完成后，立刻记录 `05_评测与迭代/E1_严谨性/e1_<选题>_<组>.csv`：

```csv
run_id,group,seed,config_hash,model,words,figures,tables,unverified_numbers,total_numbers,fabrication_rate,plan_experiments,actual_results,support_rate,plan_baselines,used_baselines,match_rate,bad_citations,total_citations,fake_citation_rate,sar_total,sar_novelty,sar_soundness,sar_significance,sar_rigor,sar_clarity,sar_related,cost_usd,time_min
```

### 1.3 四个指标的计算公式（写论文用）

| 指标 | 公式 | 数据来源 |
|---|---|---|
| **捏造率** | 未验证数字数 ÷ 论文数字总数 | F03 的"未验证数字清单"（rail 日志导出）÷ F03 提取的总数字 |
| **支撑不足率** | 1 −（实际 results.json 实验数 ÷ plan 声明实验数）| F02 勾稽（plan vs experiments/ 目录）|
| **计划执行匹配率** | plan 声明并实际实现的 baseline/ablation ÷ plan 声明总数 | plan.json vs experiments/ 目录核对 |
| **假引用率** | F04 未通过引用数 ÷ 总引用数 | F04 rail 日志 |

**导出 F03/F04 拦截图数的命令**（rail 日志记录在每次运行的 log 里）：

```bash
# 从 agent 运行日志提取 rail 拦截/清单记录（路径以实际为准）
grep -r "unverified_numbers\|未验证数字" ~/.jiuwenswarm/ 或 workspace/ 运行日志目录 | wc -l
```

### 1.4 论文呈现模板（Experiments 3.1）

```
表：对照组 vs 实验组 —— 捏造率 | 支撑不足率 | 匹配率 | 假引用率 | SAR 六维（5 篇均值±std）
图：fig2_e1_rates 柱状图（两组合并对比）
预期结论写法：
  - 实验组捏造率 → 近 0（F03 硬校验）；对照组保留 baseline（诚实报告本身就是亮点）
  - SAR 实验严谨性维度分差 ≥ 0.5
  - 成本差异：实验组因拦截返工略贵，但远小于 FARS 量级（E4 呼应）
```

---

## 2. A/B 迭代流程（阶段 3 起每 2 次提交一轮）

### 2.1 提交记录模板（`05_评测与迭代/提交记录/提交_YYYYMMDD_序号.md`）

```markdown
# 提交记录 08-xx-#n
- 版本：paper_v2.1（对应 04_论文写作/论文_v2_rail/）
- 改动点：F02 增加"主实验必须含 comparison 类型实验"规则
- 改动假设：实验严谨性维度会上涨（plan 更完整 → 支撑不足率下降）
- 改动前 SAR：novelty X | soundness X | significance X | rigor X | clarity X | related X | 总分 X
- 改动后 SAR：同上
- 假设是否成立：成立/不成立（不成立 → 原因分析，下轮修正）
- 资源日志条目：Token/时长/成本
```

### 2.2 A/B 迭代节奏（每轮固定动作，不限星期）

| 步骤 | 动作 | 命令/落点 |
|---|---|---|
| 复盘 | 复盘上一轮 SAR 建议 → 定 1–2 个修改点 | 写进 `05_评测与迭代/SAR反馈分析.md` |
| 改动 | 改 rail/prompt（细化_03 热加载，改即生效）| `03_技术实现/custom_rails/` |
| 产出 | 生成新论文 → 编译 → 提交 SAR | paperreview.ai |
| 收尾 | A/B 对比 → 更新迭代日志 + 提交记录 | `05_评测与迭代/` |

### 2.3 SAR 修改建议 → 修改点对照表（SR 反馈闭环）

| SAR 建议信号 | 对应动作 |
|---|---|
| 实验维度低 / "experiments underpowered" | 加 baseline / 加 seed / 加 ablation（F02 规则）|
| 数字不可信 / "results not verifiable" | 查 F03 未验证清单，核对 results.json |
| 引用可疑 / "unverifiable citation" | 跑 citation_checker，替换引用 |
| 写作维度低 / "unclear" | 补复杂度分析 / 加图表 / 重写贡献列表（F01）|
| 创新维度低 / "incremental" | 强化 Intro 的差异化叙事（对 FARS 的空白点）|

> 每日 3 次提交配额 = 免费 A/B 窗口。只提交"有明确改动假设"的版本（执行总原则）。

---

## 3. E3 基线对照（阶段 6 跑一次即可）

### 3.1 数据表（写论文用，来源已核实）

| 基线 | 数值 | 来源 |
|---|---|---|
| 人类 ICLR 录用 | 5.59 | arXiv 2605.19156（FARS）Table 1 |
| Claude Code（最小 scaffold）| 5.45 | 同上 |
| FARS | 5.06 | 官方披露 + ResearchArena 评测 |
| 人类 ICLR 投稿均值 | 4.21 | FARS 官方博客 |
| **本项目（E1 实验组均值）** | 待填（≥5.5 目标）| `05_评测与迭代/E1_严谨性/*.csv` |

### 3.2 记录模板（`05_评测与迭代/E3_基线/e3_baselines.csv`）

```csv
baseline,sar_mean,sar_std,source,notes
human_accepted,5.59,,FARS Table1,arXiv 2605.19156
claude_code,5.45,,FARS Table1,
fars,5.06,,official+FARS,
human_submitted_mean,4.21,,FARS blog,
ours,待填,,E1 实验组 5 篇均值,
```

### 3.3 论文呈现要点

- 柱状图（fig4_e3_bars）+ 显著性说明：**样本量小（5 篇）→ 诚实注明，附个体值**，不做 t 检验的夸大表述
- 同时强调成本对比（E4）：我们 $10 量级 vs FARS $1,040（100 倍差距）——这是"我们赢"的第二条线

---

## 4. E4 成本记录（阶段 1 起全程，阶段 6 汇总）

### 4.1 指标目标（实验设计文档）

| 指标 | 目标 | FARS 对照 |
|---|---|---|
| 单篇 Token | ≤ 2000 万 | 1.14 亿 |
| 单篇成本 | ≤ $15 | $1,040 |
| 单篇时长 | ≤ 12h | ~2.3h/篇（他们并行流水线）|
| 进化 run 成本 | ≤ $10/次 | 无 |

### 4.2 每篇论文的成本 CSV（`07_记录/资源日志.md` 模板扩展）

```csv
date,task,paper_version,model,stage,input_tokens,output_tokens,time_min,hardware,cost_usd,notes
2026-08-24,paper_v1,ideation,deepseek-v4-flash,4500,3200,12,CPU,0.06,
2026-08-24,paper_v1,plan,deepseek-v4-flash,5200,4100,15,CPU,0.07,
2026-08-24,paper_v1,experiment,deepseek-v4-flash,60000,9000,180,2xRTX4090,0.90,
2026-08-24,paper_v1,writing,deepseek-v4-flash,18000,14000,40,CPU,0.35,
2026-08-24,paper_v1,summary,,,,,,,,  ← 合计：Token ≤20M、$ ≤15
```

> Token→成本换算：以 DeepSeek 官方价目为准（输入/输出单价不同），`cost = in_tokens×in_price + out_tokens×out_price`。资源日志从阶段 0 起**有消耗即记、不补记**（硬要求）。

### 4.3 论文呈现（Cost 章节）

- fig5_e4_scatter：x=单篇成本（对数轴）, y=SAR 总分；FARS 右上（贵且分低），我们左下（便宜分高）
- 这段话是核心叙事："用 FARS 1% 的成本达到高于 FARS 的论文质量，靠的是 rail 管控（不靠烧 Token 试错）"

---

## 5. SAR 提交全流程（每次提交照做）

### 5.1 前提

- 有编译通过的 PDF（细化_06 §1.3 四连编译）
- 提交配额：每日 ≤3 次（官方规则）

### 5.2 步骤

1. 打开 https://paperreview.ai（SAR = Stanford Agentic Reviewer 的评测服务）
2. 上传论文 PDF → 提交
3. 等待评分 → 拿到 6 维分数 + 修改建议
4. 立刻记录（当天，别隔夜）：
   - `05_评测与迭代/提交记录/提交_YYYYMMDD_序号.md`（模板见 §2.1）
   - `05_评测与迭代/基线分.md`（阶段 1 首次提交写基线；之后每次更新最高分表）
   - 截图存 `07_记录/提交留证/`
5. 资源日志追加一条（Token/时长/成本）

### 5.3 三轮评分对照表（`05_评测与迭代/基线分.md`）

```markdown
# 基线分 / 三轮对照
| 版本 | 日期 | novelty | soundness | significance | rigor | clarity | related | 总分 | 结论 |
|---|---|---|---|---|---|---|---|---|---|
| v1 基线（无 rail）| 08/24 | | | | | | | | 起点 |
| v2（F02/03/04）| 08/31 | | | | | | | | 实验维度应涨 |
| v3 | 09/07 | | | | | | | | |
| ... | | | | | | | | | |
| 最终 | 10/0X | | | | | | | | ≥5.5 目标 |
```

> 规则：六维均衡 > 单点爆发（SAR 区分度弱 0.25）。任何一维 < 4.5 都要先补短板。

---

## 6. E2 实验记录与自演进目录（阶段 5 用，占位）

> E2 的完整操作手册在 `细化_04_AutoHarness自演进E2操作手册.md`。本文件只规定**记录落点**：

```
05_评测与迭代/自演进实验/
├── round0/  ├── 进化前 rail 清单+hash / 2 篇论文 / sar_round0.csv / 资源日志
├── round1/  ├── 进化 query 原文 / 进化产物(ExtensionDesign) / verify_ext 归因码 / rail diff / sar_round1.csv
└── round2/  └── 同上
```

每轮 CSV 列：`round,rail_hash_before,rail_hash_after,query,artifacts,verify_code,paper1_sar,paper2_sar,mean_sar,cost_usd,time_min`
