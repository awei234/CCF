# 细化 04：Auto Harness 自演进 E2 操作手册（阶段 5 手把手）

> 对应：原理_02（机制）+ 行动_自演进实验设计 §E2。
> 解决的问题：**Auto Harness 怎么配？E2 三轮进化怎么跑？每轮记什么？失败怎么办？PR 怎么提？**
> ⚠️ 标注「待实测」的步骤以阶段 5 实测为准（原理_02 §9 待测清单）。
> 🔧 **2026-08-12 源码核查修正**：Auto Harness 配置路径实测为 **`~/.jiuwenswarm/auto-harness/config.yaml`**（jiuwenswarm `service.py:72,239`，`get_user_workspace_dir()` = `~/.jiuwenswarm`），**不是** 原理_02 写的 `~/.openjiuwen/auto_harness/config.yaml`。后者是 openjiuwen（agent-core）侧的文档假设，本工作区源码不支持。配置字段中 `agent`/`extensions`/`fix_loop` 段在本仓库 service 未被读取（归外部 `openjiuwen.rsi.auto_harness.schema` 所有）→ 标为「待实测」。
> 更新日期：2026-08-12（细化批）

---

## 0. 前置检查（进阶段 5 前必须全绿）

| # | 检查项 | 验证命令 | 通过标准 |
|---|---|---|---|
| 1 | 服务器 venv 有 openjiuwen | `source ~/CCF/.venv/bin/activate && python -c "import openjiuwen; print(openjiuwen.__version__)"` | 打印版本号 |
| 2 | DeepSeek 可调 | `jiuwenswarm chat "hello"` | 有应答 |
| 3 | F02/F03/F04 已热加载 | 细化_03 §6 的 verify 命令 | 输出 4 行 enabled |
| 4 | git 身份已配 | `git config --global user.name && git config --global user.email` | 非空 |
| 5 | GitCode token 已配 | `echo $GITCODE_ACCESS_TOKEN` | 非空（阶段 0 已申请）|

> 若第 5 项为空：阶段 0 步骤（细化_01 阶段 0）重新配置。Meta pipeline 必须 token；Expert pipeline 不必须。

---

## 1. Auto Harness 配置（`~/.jiuwenswarm/auto-harness/config.yaml`）

> ⚠️ 路径已修正（见文首）：`~/.jiuwenswarm/auto-harness/config.yaml`，数据目录 `~/.jiuwenswarm/auto-harness/`（run 日志也在其下 `runs/{task_id}/{execution_id}/log.json`）。本地 Windows 对应 `C:\Users\<用户名>\.jiuwenswarm\auto-harness\`。

### 1.1 首先生成文件

```bash
# 服务器：openjiuwen 侧配置由服务自动引导创建；手动建目录+文件也可
mkdir -p ~/.jiuwenswarm/auto-harness
# 首次 /auto-harness 若提示缺配置，按提示补 user_name/user_email 即可
```

### 1.2 完整配置内容（已验证字段 + 待实测字段分开标）

```yaml
# ~/.jiuwenswarm/auto-harness/config.yaml
# ✅ = 本仓库 service/config_validator 已验证读取的字段；❓ = 来自上游 schema 文档，待实测

git:
  base_branch: "develop"            # ✅ 未设置时强制 develop（service.py:757）
  git_remote: "origin"              # ✅ 默认 origin（service.py:761）
  user_name: "vergil"               # ✅★必填（ConfigValidator REQUIRED_FIELDS；联动写 fork_owner/gitcode.username）
  user_email: "vergil@example.com"  # ✅★必填
  fork_owner: "vergil"              # ✅ 缺省写 user_name
  upstream_owner: "openJiuwen"      # ✅ 上游（不动）
  upstream_repo: "agent-core"       # ✅ 上游（不动）

gitcode:
  username: "vergil"                # ✅
  access_token: ""                  # ✅ 可选；环境变量 GITCODE_ACCESS_TOKEN 可替代（推荐用环境变量）

local_repo: ""                      # ✅ 默认 <data_dir>/repo/openJiuwen--agent-core（留空即可）

budget:
  session_secs: 900000              # ❓ 上游文档字段（本仓库 service 读 max_tasks_per_session）
  cost_limit_usd: 10.0              # ❓ 单会话成本上限 $10（E4 目标）
  task_timeout_secs: 300000         # ❓
  model_timeout_secs: 300000        # ❓
  max_tasks_per_session: 5          # ✅ service 读取（默认 5，封顶 5）

ci_gate:
  config_path: ""                   # ✅ 空=默认
  python_executable: ""             # ✅ 默认 sys.executable（用 venv python）
  install_command: ""               # ✅ 默认 "uv sync --active --group dev --extra cli"

# ❓ 以下段来自 openjiuwen.rsi.auto_harness.schema（上游），本仓库 service 不读取——
#    保留自 原理_02 的 72 行文档字段，阶段 5 实测后按真实行为取舍：
fix_loop:
  phase1_max_retries: 10            # ❓ verify 失败自动修复上限
  phase2_max_retries: 9             # ❓
agent:
  implement: 60                     # ❓ assess/plan/implement max_iterations
extensions:                          # ❓ 源码贡献注册点（§5 PR 用）
  stage_registrars: []              # ❓ module:callable
  pipeline_registrars: []           # ❓ module:callable
```

### 1.3 必填校验（ConfigValidator）

| 字段 | 状态 |
|---|---|
| `git.user_name` | ★必填；写入时联动写 `git.fork_owner` + `gitcode.username` |
| `git.user_email` | ★必填 |
| `gitcode.access_token` | 可选（环境变量 `GITCODE_ACCESS_TOKEN` 可替代）|

> 也可用 TUI 编辑：`/config edit`（项：`auto_harness_git_user_name / auto_harness_git_user_email / auto_harness_gitcode_access_token`）或 `/status config` 查看。

### 1.4 待实测确认项（阶段 5 第一天做）

- [ ] 配置文件实际路径与自动引导行为（按修正后路径 `~/.jiuwenswarm/auto-harness/` 确认）
- [ ] `cost_limit_usd` 触发熔断的真实行为（超 $10 会怎样停）
- [ ] `agent`/`extensions`/`fix_loop` 三段是否需要保留（对照 openjiuwen 实际 schema）

---

## 2. 先小 query 试跑（阶段 5 第 1–2 步，跑通流程再上实验）

### 2.1 最小试跑命令

```bash
# 服务器 TUI 内（或对应 CLI 入口）
/auto-harness run --pipeline optimize_expert_harness \
    "评估科研严谨性扩展包的当前缺口（不需要实现改动，只输出评估报告）"
```

### 2.2 观察点（对着原理_02 §3.3 的阶段流）

```
assess(gap) → select_pipeline → design_ext → implement_ext → verify_ext → build_verify → merge → activate
```

每过一个阶段，确认：
- assess：输出 GapAnalysisArtifact（差距表：竞品/功能/当前状态/差距/影响/可行性/建议方案/目标文件）
- select_pipeline：**固定选中 extended**（prompt 强制 `pipeline_name=extended_evolve_pipeline`）
- design_ext：产出 ExtensionDesign 列表（persist 到 `extension_design_*.json`）
- implement_ext：生成 `openjiuwen/extensions/harness/<name>/`（tools/rails/skills/requirements.txt/harness_config.yaml）
- verify_ext：L1 结构 / L2 临时 DeepAgent 热加载 / L3 行为验证
- activate：**用户确认 → 热加载激活 → 生成 Harness Package**（`__interaction__`；auto_accept 时自动激活）

### 2.3 日志查看（失败时排查）

```bash
# 运行日志落盘（JSON Lines）
ls ~/.jiuwenswarm/auto-harness/runs/{task_id}/{execution_id}/log.json
# 状态机：pending → running → success|failed|cancelled
```

---

## 3. E2 三轮进化实验（阶段 5 第 3–7 步）

### 3.1 每轮流程（Round 0 是基线，不触发进化）

```
Round 0（基线）:
  当前 rail 配置 → 生成 2 篇论文（选题用 E1 选题池的前 2 个）→ SAR 记录
       │
       ▼ 进化触发
Round 1:
  /auto-harness run --pipeline optimize_expert_harness "<query 模板 A>"
  → 产物：新 rail/tool → verify_ext → 热加载激活
  → 用新 rail 配置生成 2 篇论文 → SAR 记录 → 对比 Round 0
       │
       ▼
Round 2:
  /auto-harness run --pipeline optimize_expert_harness "<query 模板 B（附 Round1 结果）>"
  → 生成 2 篇论文 → SAR 记录
```

### 3.2 query 模板全文

**Round 1 query 模板：**

```
分析最近 2 篇论文的 SAR 反馈（附 6 维分与修改建议）。
评估科研严谨性扩展包的缺口，设计并实现改进（可新增/修改 rail、tool、skill），
热加载生效。要求：
1. 优先针对 SAR 分数最低的维度改进；
2. 硬约束独立建模为 kind="constraint" 的 rail；
3. 保持 F02/F03/F04 现有功能不回退；
4. 产物必须通过 verify_ext（L1 结构 / L2 热加载 / L3 行为）。
```

**Round 2 query 模板（附 Round 1 结果）：**

```
附上 Round 1 的进化结果：进化前 rail 清单 hash=X，进化后 diff=Y，验证归因码=Z，
2 篇新论文 SAR=（六维各值，均值=W）。
请分析本轮进化的效果：SAR 是否提升？哪一维提升/下降？
针对仍未改善或新出现的缺口再设计一轮改进（可新增/修改 rail、tool、skill），
热加载生效，同样要求通过 verify_ext 且不回退 F02/F03/F04。
```

### 3.3 每轮记录（存 `05_评测与迭代/自演进实验/roundN/`）

**roundN/record.csv**（列固定）：

```csv
round,rail_hash_before,rail_hash_after,query,artifacts,verify_code,paper1_sar,paper2_sar,mean_sar,cost_usd,time_min
```

**roundN/进化前_rail清单.md**（人工/脚本生成）：
- rail 名 + priority + 关键参数 + 文件 hash（`sha256sum`）

**roundN/进化后_rail清单.md**：
- 与进化前 diff（`diff` 输出粘贴）+ 新增/修改的文件清单

**roundN/verify归因码.md**（若 verify_ext 失败）：
- 归因码 + 处理动作（见 §4.2 表）

### 3.4 论文呈现素材（每轮存一份，阶段 6 直接用）

```
表：Round 0 → 1 → 2 的 SAR 六维变化（实验维度/写作维度预计上升）
图：自演进闭环架构图（assess → design → implement → verify → activate → 再评测）
案例：选出"改了什么 rail、为什么、效果如何"最清晰的一轮写进论文
（例：Round 1 发现 F02 未强制新 baseline → 自动加规则 → 相关工作维度分提升）
```

---

## 4. 失败预案决策树（E2 的命脉，阶段 5 反复对照）

### 4.1 决策树

```
/auto-harness run 失败？
├─ 配置问题（assess 都起不来）
│   └─ 对照 §1 配置逐项检查（git 身份/token/budget）→ 重跑
├─ assess/design 出报告但 implement 失败
│   └─ verify_ext 归因码 → §4.2 表处理 → fix_loop 会自动重试（phase1 10 次）
├─ verify_ext 通过但 activate 失败
│   └─ 检查热加载路径/权限 → 手动激活（Web 端"激活"操作，待实测）
├─ 进化成功但新论文 SAR 没涨
│   └─ ★本身就是发现：诚实报告"该轮进化无增益 + 归因分析"（SAR 对负结果友好）
└─ 阶段 5 结束前无法产出可用 E2 数据
    └─ 切 T04 主叙事：E2 用"人工改进 rail 的 A/B 对比"替代（E1 增强版）
       自演进写 Future Work。决策记录写进 05_评测与迭代/提交记录/
```

### 4.2 verify_ext 归因码处理表

| 归因码 | 含义 | 处理动作 |
|---|---|---|
| `manifest_invalid` | harness_config.yaml 格式错 | 让 Auto Harness 重写 manifest（fix_loop 会自动做）；仍失败 → 手动修 schema_version: harness_config.v0.1 |
| `entry_point_not_allowed` | 入口点不被允许 | 检查 rail 类名/注册路径是否符合规范（细化_03 §6）|
| `module_import_failed` | 导入失败 | 检查依赖：扩展的 requirements.txt 是否在 venv 装齐 |
| `class_init_failed` | rail 类初始化失败 | 检查 `__init__` 签名（继承 DeepAgentRail 不要自定义必填参数）|
| `skill_manifest_invalid` | skill 的 SKILL.md frontmatter 错 | 对照细化_02 §1 的 frontmatter 字段 |

### 4.3 E2-lite 半自动替代（确定性更高的方案）

若全自动闭环不稳，退化流程（数据可靠，叙事弱一些）：

```
1. 人工把 SAR 反馈整理成结构化建议（六维分 + 修改点）
2. 用 skill 引导 agent：读建议 → 设计 rail 改进 → 热加载（人工执行 verify）
3. 记录"反馈 → 改进 → 验证"数据（record.csv 结构不变）
4. 论文中如实写"人工辅助的自演进闭环"（Human-in-the-loop evolution）
```

---

## 5. Meta pipeline 提 PR（框架贡献交付物）

### 5.1 前置

- GitCode 有账号 + fork 了上游仓库（openJiuwen/agent-core）
- `GITCODE_ACCESS_TOKEN` 环境变量可用（阶段 0 已配置）

### 5.2 流程

```bash
# 1. 触发 Meta pipeline（让系统评估并改进底座）
/auto-harness run --pipeline optimize_meta_harness \
    "为科研场景增加一个 paper_consistency_check Stage（注册进 extended pipeline），
     并补单元测试，按规范提 PR。"

# 2. 全程观察（assess→plan→implement→verify→commit→publish_pr→learnings）
#    verify 阶段注意 CI gate：make check / make type-check 必须过；immutable_files 不可改

# 3. publish_pr 阶段 → fork push → GitCode PR 模板创建（/kind feature）
#    拿到 PR 链接 → 存入 06_提交物/框架贡献/
```

### 5.3 PR 备选方向（原理_02 §7，从易到难）

| # | 方向 | 难度 | 服务对象 |
|---|---|---|---|
| 1 | 新增科研专用 Stage（如 `paper_consistency_check`）| 中 | 自演进能力展示 |
| 2 | 新增 verify_ext 验证器（PDF 头/JSON schema/数字勾稽）| 中 | 与 F03 呼应 |
| 3 | assess 增加 `research_gap_assessment` 评估模式（读 SAR 反馈）| 中 | E2 增强 |
| 4 | 补文档 + 单测（`tests/unit_tests/auto_harness/`）| 低 | 合规保底 |

> 若 Auto Harness 提 PR 全链路不稳（待实测），兜底：人工把 rail 代码整理成提交提 PR（细化_06 §6 ④ 框架贡献说明）。

### 5.4 待实测确认项

- [ ] Meta pipeline 从 fork push 到 PR 创建的全链路（需 GitCode token）
- [ ] 扩展注册点 `extensions.stage_registrars / pipeline_registrars` 的真实行为

---

## 6. 风险与预算红线速查

| 风险 | 缓解 |
|---|---|
| 一次 run Token 不小 | `budget.cost_limit_usd: 10.0` 硬红线；先小 query 试跑再上实验 |
| 多步 agent 交互中途失败 | fix_loop 自动修复兜底；scheduler 日志可查（§2.3）|
| 环境门槛 | 先 Expert 层（不碰 CI/PR），Meta 层放 PR 环节再配 token |
| 时间 | E2 窗口（阶段 5 内）；不成 → §4.1 决策树切 T04 |
