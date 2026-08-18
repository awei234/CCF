# CCF BDCI 2026 · 华为 openJiuwen 赛题 · 参赛工作区

> **赛题**：【华为 openJiuwen】基于 JiuwenSwarm 的 Agent 科研论文自动生成
> **官网**：https://www.xir.cn/competition/1167 ｜ **评测**：https://paperreview.ai（SAR）
> **整理日期**：2026-08-11 ｜ **阶段化更新**：2026-08-17 ｜ **当前赛程**：初赛第二轮（08/01–08/31），第三轮 09/01–10/09 截止

---

## 一、一句话定位

**用「轻资产 + Rail 增强 Harness + 严谨实验」路线，实现 SAR ≥ 5.5（折算 ≥ 22 分）的自动科研系统，进 TOP5 决赛，冲击奖项，并完成合规源码贡献（PR + 开源）。**

> 核心情报：FARS 标杆 5.06 分 / $1,040 每篇，最小 scaffold 反而 5.45 分 / $9 每篇（arXiv 2605.19156）——**重资产不是优势，严谨实验 + 工程化管控才是差异点**。

---

## 二、目录导航

| 目录 | 内容 | 入口 |
|---|---|---|
| **00_比赛总览** | 目标 / 官方规则 / 评分拆解 / 赛程里程碑 / 现状差距 / 行动路线 | `00_比赛总览/比赛目标.md` |
| **01_方向库** | **全部 18 个方向**（D 实现路线 5 + T 论文主题 6 + F 功能模块 7）+ 对比矩阵 | `01_方向库/README.md` |
| **02_情报库** | FARS 全文 + 优化映射 / SAR 机制 / 框架速查 / 文献总结 | `02_情报库/FARS标杆分析/FARS四局限与优化映射.md` |
| **03_技术实现** | JiuwenSwarm 源码副本 + custom_skills/ + custom_rails/ + prompts/ | `03_技术实现/README.md` |
| **04_论文写作** | ICLR 模板 / 论文草稿 / 图表素材 | `04_论文写作/README.md`（v1–v6 论文）|
| **05_评测与迭代** | SAR 提交记录 / A_B 实验日志 | `05_评测与迭代/README.md` |
| **06_提交物** | 技术包 / 资源报告 / 框架贡献说明（四件套）| `06_提交物/提交物清单.md` |
| **07_记录** | 资源日志 / 迭代日志 | `07_记录/README.md` |

---

## 三、推荐主线（决策结论）

```
实现路线：D05 混合架构（D01 skill 流水线 → D03 rail 管控 → D04 自演进）
论文主题：T03 Agent 自演进（主） + T04 实验严谨性（副）
功能模块：第一批 F02+F03+F04（实验三件套）→ 第二批 F01+F06+F07 → 第三批 F05

论文主线一句话：
「Rail-Augmented Harness for Rigorous and Self-Evolving Agentic Research」
用 Rail 增强 Harness，实现严谨、自演进的自动科研——直接对应 FARS 论文 §6 的空白
```

**决策依据**：官方进阶思路（改源码 + rail 拓展 harness）= 合规硬性要求 = 方法合理性维度 = 差异化核心，三合一。

---

## 四、当前进展（阶段 3 A/B 迭代 / v7 冲刺）

> 详见 `00_比赛总览/从零开始行动路线.md`；阶段制手册见 `01_方向库/深度方案_T03_D05/细化_01_阶段执行手册.md`

1. ✅ 阶段 0/1/2 完成：环境、最小闭环、F02/F03/F04 rail（单测 16/16）
2. ✅ SAR 已提交 v1–v6：峰值 **5.8**（v1/v3/v5/v6），当前短板 Writing_Clarity 已回 +1，瓶颈转向“full-rail 相对强提示/单门控的独特价值 + 跨模型 + UCR 激活”
3. 🔄 阶段 3 A/B 迭代进行中：v6 已出分，v7 实验（T4 执行声称 + DeepSeek/GLM/Qwen 跨模型 + 组合消融）脚本已就绪
4. ⚠️ 服务器根分区紧张：大文件放 `/data`（约 20T 可用）

> **当前主攻：v7 = T4 执行声称压力任务 + 跨模型 + 组合消融，目标 SAR 6+**

---

## 五、关键链接

| 内容 | 链接 |
|---|---|
| 比赛详情 | https://www.xir.cn/competition/1167 |
| SAR 评测 | https://paperreview.ai |
| JiuwenSwarm 仓库 | https://atomgit.com/openJiuwen/jiuwenswarm |
| 快速上手 | https://atomgit.com/openJiuwen/jiuwenswarm/blob/develop/docs/zh/Quickstart.md |
| 技术答疑 | https://gitcode.com/openJiuwen/jiuwenswarm/discussions/13 |
| 获奖开源仓库 | https://gitcode.com/openJiuwen/agent-store |

## 六、硬性时间锚点（官方）

| 锚点 | 时间 |
|---|---|
| 初赛第二轮提交 | 08/01 – 08/31（每日每队最多 3 次）|
| 初赛第三轮 | 09/01 – 10/09 |
| **最终提交截止** | **10/09 24:00** |
