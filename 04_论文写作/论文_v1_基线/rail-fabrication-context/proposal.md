# 校验 Rail 对 LLM 科研 Agent 捏造率的抑制：上下文工程方向的受控实验（研究提案）

## Introduction

### 背景
LLM 科研 Agent（如自动选题→规划→实验→写作的 research pipeline）正在进入真实科研流程。随之而来的核心信任问题是**捏造（fabrication）**：生成不存在的引用、与实验结果无关的数字、以及从未执行过的实验声称。该问题已被大范围实证：

- 对 111M 条引用（arXiv/bioRxiv/SSRN/PMC 共 2.5M 篇论文）的审计发现 2025 年新增幻觉引用约 146,932 条（wildhallucinations2026）。
- NeurIPS 2025 录用集中检出 53 篇含幻觉引用的论文（GPTZero，转引自 hallmark2026）。
- 10 个商用 LLM 在 4 个学术领域生成 69,557 条引用，幻觉率在 11.4%–56.8% 之间，且**无模型在未被提示时自发生成引用**——即捏造是提示/上下文诱导的，而非模型固有属性（howllmscite2026）。

### 问题陈述
现有缓解手段可分为三类，但都未回答一个因果问题：

1. **事后检测**：CiteAudit / CiteTracer / HALLMARK 等验证器在稿件生成后筛查捏造引用。它们能定位问题，但**不阻止捏造发生**，且验证器自身的误报率（FPR）是部署瓶颈（hallmark2026）。
2. **架构提案**：HALO 提出"零幻觉是系统强制属性而非模型属性"的六层防线（halo2026）；Theoria 用可审计状态迁移验证推理（theoria2026）。它们论证充分，但缺少在统一科研任务上的受控、多种子实验证据。
3. **相关性测量**：ProofAgent-Harness 证明上下文质量（grounding sufficiency 等 7 维）能预测 agent 的幻觉抵抗力，但这是**相关性**而非干预性因果（contextfailsfirst2026）。

### 关键洞见
Rail 本质上是一种**上下文工程手段**：它在 Agent 的工作流关键节点（plan→results→paper）注入**验证契约**（verification contract），把"诚实"从模型的自愿属性变成系统强制的流程属性。本 skill 自身即声明了这样的实验配置：E1 对照组 = 无 rail；实验组 = 本 skill + F02/F03/F04 rail（plan.json 结构校验、results.json 勾稽、引用核验）。这恰好构成一个天然的受控实验台：**在完全相同的 skill 与任务下，只改变 rail 的有无，测量捏造率的变化**。

### 假设
- **H1（主假设）**：注入校验 rail（F02/F03/F04）比无 rail 基线显著降低科研任务的捏造率（引用捏造率、数字捏造率、未执行实验声称率），且不显著损害任务完成度与成本效率。
- **H2（机制假设）**：rail 的抑制效果来自**验证契约-打回重做的流程门控**，而非仅靠提示注入；全量 rail 优于单一组件，单组件优于"请勿捏造"式提示基线。
- **H3（边界假设）**：抑制效果随模型能力与任务复杂度变化——弱模型受益更大，任务越开放（写作）比越封闭（结构化 plan）的捏造率抑制空间越大。

## Proposed Approach

### 概述
以 research-pipeline skill 为实验台，把 rail 视为上下文工程的**流程级干预**：

- **F02（plan.json 校验）**：在规划阶段强制结构契约——实验 ≥3、每实验 baseline ≥2、seeds ≥3、ablation 前置、budget 估算、含 reproducibility。不达标打回重做。
- **F03（results.json 勾稽）**：在执行与写作阶段强制数据契约——plan 声明的每个实验必须有 results.json；论文中每个数字必须有 results.json 出处。无出处数字被标记并要求修正或删除。
- **F04（引用核验）**：写作阶段强制引用契约——每个 `\cite{}` 必须在 references/ 池命中，池内文献必须真实可在线核验。不在池中的引用被拒绝。

### 方法细节
- **捏造率指标**（可自动计算）：
  - *Citation Fabrication Rate (CFR)*：生成引用中无法在真实文献池/在线核验中命中、或与声明内容不符的比例。
  - *Numeric Fabrication Rate (NFR)*：论文/报告数字中无 results.json 出处或与 results 推导不符的比例。
  - *Unexecuted Claim Rate (UCR)*：声称已执行的实验无对应 results.json / 日志的比例。
- **实验条件**：同一批任务、同一模型、同一批种子（≥3），仅切换 rail 装配（无 rail / 提示式 / 全量 rail / 单组件 rail）。
- **任务集**：结构化生成任务（科研 proposal + plan）与半开放写作任务（paper 章节含引用与数字）两级，覆盖 H3。

### 关键创新
1. 首次把"校验 rail"作为**上下文工程的受控干预变量**做因果实验（此前只有检测器、架构、相关性三类工作）。
2. 定义可自动计算、可复现的**捏造率指标族**（CFR/NFR/UCR），与 F03 勾稽机制同构，便于审计。
3. 机制消融（门控 vs 提示）首次分离"流程强制"与"上下文劝导"两种防捏造路径的贡献。

## Related Work

- **上下文工程作为可靠性手段**：contextfailsfirst2026（上下文质量预测可靠性）、llorir2026（去噪优先，可验证性是瓶颈）、trace2026（轨迹归因自动修复上下文）、deepagenticsearch2026（子代理隔离上下文防 context rot，但引入静默交接失败）。与我们的差异：它们测量或修复上下文质量，我们**干预**流程级校验契约并测捏造率因果。
- **引用/数字捏造检测**：citeaudit2026、citetracer2026、hallmark2026、wildhallucinations2026、howllmscite2026、legalcitations2026。与我们的差异：检测器是事后筛查，我们是**事前流程门控**，且把"捏造率"当作被干预的因变量而非筛查目标。
- **系统级防幻觉架构**：halo2026（六层防线，架构论述）、theoria2026（可审计状态迁移验证）、prompttopaper2026（确定性 RAG + 真实实验执行 + 幻觉惩罚）、phantomfill2026（表单强制字段驱动捏造→逃生 token）、failuremodes2026（F1 引用捏造 / F2 前提走私分类）。与我们的差异：它们各自提出新组件或新分类，缺少"在既有 skill 上做 rail 有/无受控对比"的简洁实验设计。
- **定位**：Unlike 上述工作，我们不做新检测器、不提出新架构组件，而是把本 pipeline 已有的 F02/F03/F04 rail 当作上下文工程干预，回答"流程级验证契约到底能把捏造率压到多低、代价是什么"这一此前无人用受控多种子实验回答的问题。

## Experiments

计划实验（详细预算与种子见阶段 2 plan.json）：

| 实验 | 类型 | 内容 | 关键对比 |
|---|---|---|---|
| exp1 | comparison（主实验） | 无 rail vs 提示式 vs 全量 rail（F02+F03+F04），同一任务集，3 seeds | H1：CFR/NFR/UCR 显著下降？ |
| exp2 | ablation | 单组件 rail（仅 F04 / 仅 F03 / 仅 F02）与全量对比 | H2：门控 vs 提示、组件贡献排序 |
| exp3 | scaling | 不同模型（弱/强）与任务复杂度（结构化/开放写作） | H3：受益边界 |
| exp4 | analysis | 成本-质量权衡：迭代轮数、token 成本 vs 捏造率降幅 | 负面代价分析 |

**基准（baselines）**：
- 简单 baseline：无 rail 的原始 skill 流程（E1 对照组）。
- 强/新近 baseline：提示式防捏造（在上下文中注入"禁止捏造引用/数字，不确定就说明"的强指令），对应 howllmscite2026 观察到的提示诱导性——验证纯提示是否足够。

**指标**：CFR / NFR / UCR（降幅）、任务完成度（success rate）、成本（迭代轮数、token）。

**预期结果**：全量 rail 组 CFR/NFR 显著低于无 rail 组（目标 Δ≥10pp，3 seeds 方向一致）；提示式介于两者之间或接近无 rail（若提示不足，则支持 H2 门控机制）；弱模型受益更大（支持 H3）。

## Success Criteria

- **H1 证实**：全量 rail 组 CFR/NFR/UCR 显著低于无 rail 基线（配对检验 p<0.05，3 seeds 全部同向），完成度无显著下降。
- **H1 证伪**：rail 组与无 rail 组捏造率无显著差异，或 rail 组更高；或完成度显著恶化到不可用。
- **H2 证实**：全量 rail ≥ 单组件 ≥ 提示式 ≥ 无 rail（捏造率单调递减）；提示式若接近无 rail，则证明纯提示不足、门控必要。
- **H3 证实**：弱模型或开放写作任务的降幅显著大于强模型或结构化任务。
- 诚实执行：若某实验跑不通或结果相反，如实记录负结果（SAR 对负结果友好），不静默砍实验。

## References

全部引用池见 `references/`（每篇含 meta_info.txt / bibtex.txt / abstract.md，均可在线核验）：

1. Reizinger & Brendel (2026) — HALLMARK: Diagnosing Three Failure Modes in LLM Citation Verifiers. arXiv:2607.18360
2. Raduta et al. (2026) — Zero Hallucination, by Construction: HALO. arXiv:2607.17883
3. Bousetouane (2026) — AI Agents Do Not Fail Alone: The Context Fails First. arXiv:2607.14275
4. Zhao et al. (2026) — LLM hallucinations in the wild. arXiv:2605.07723
5. Naser (2026) — How LLMs Cite and Why It Matters. arXiv:2603.03299
6. Shi et al. (2026) — CiteAudit. arXiv:2602.23452
7. Li et al. (2026) — CiteTracer. arXiv:2605.08583
8. Saldivar & Slivinski (2026) — Theoria. arXiv:2607.01223
9. Usman (2026) — PhantomFill. arXiv:2607.20492
10. Banerjee & Bhattacharjee (2026) — Failure Modes of LLMs on Research-Level Mathematics. arXiv:2606.24902
11. Ferreira da Silva et al. (2026) — Toward Trustworthy Autonomous Science: A Two-Year Community Roadmap. arXiv:2607.12113
12. Kamran et al. (2026) — Prompt-to-Paper. arXiv:2607.05456
13. Dai et al. (2026) — LLM-Oriented Information Retrieval: A Denoising-First Perspective. SIGIR 2026, arXiv:2605.00505
14. Zhao et al. (2026) — TRACE: TRajectory Attribution for Automated Context Engineering. arXiv:2608.09153
15. Rafiei Oskooei et al. (2026) — Deep Agentic Search for Repository-Level Code QA. arXiv:2608.01507
16. Shi et al. (2026) — From Sycophancy to Deception: A Unified Taxonomy. ICLR 2026 Agents in the Wild Workshop, arXiv:2604.04788
17. Alrajeh (2026) — Do LLMs Fabricate Legal Citations? arXiv:2607.11127
