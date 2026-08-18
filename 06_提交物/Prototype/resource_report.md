# Prototype 资源消耗报告

> 项目：基于 JiuwenSwarm 的 Agent 科研论文自动生成
> 版本：v6（SAR 5.8）
> 数据来源：`07_记录/资源日志.md`、各实验结果 results.json、`v5_token_usage.csv`、SAR 提交记录

## 1. 模型与运行环境

- 模型：deepseek-v4-flash（OpenAI 兼容）
- 服务器：10.182.68.242（Dell Precision 7960，2×RTX 4090，376G 内存）
- 算力：CPU 为主（LLM API 调用 + 审计），GPU 未作为主要计算资源

## 2. Token 消耗汇总（历史版本）

| 版本/阶段 | 总 Token | 备注 |
|---|---:|---|
| 阶段 0 环境/demo | ~2k | demo chat |
| 阶段 1 第一篇论文 | ~200k | ideation+实验+写作 |
| 阶段 2 v2 三臂实验 | ~800k–1.2M | 12 runs + 写作 |
| 阶段 2 v3 排版修复 | 0 | 纯本地排版 |
| 阶段 3 v4 开放池+审计 | ~600k–800k | 9 runs + 写作 |
| v5 新实验 | 见下表 | 干净T1+F02消融+T3 五臂 |
| v6 补强轮 | 0（本地编辑/编译） | T3 表、审计协议、循环性、Related Work |

## 3. v5 实验 Token 明细（来自 results.json，可追溯）

### T1（v5-clean-control）

| Arm | seed42 | seed43 | seed44 | mean±std |
|---|---:|---:|---:|---:|
| no-rail | 4857 | 5259 | 4948 | 5021 ± 211 |
| f02-only | 5379 | 5434 | 5353 | 5389 ± 41 |

### T3（v5-adversarial-T3）

| Arm | seed42 | seed43 | seed44 | mean |
|---|---:|---:|---:|---:|
| no-rail | 2300 | 2215 | 3200 | 2572 |
| prompt-only | 2100 | 2280 | 2212 | 2197 |
| f03-only | 3033 | 3034 | 2604 | 2890 |
| f04-only | 2492 | 2292 | 2319 | 2368 |
| full-rail | 3161 | 3159 | 3033 | 3118 |

## 4. 运行时长

| 阶段 | 时长 |
|---|---:|
| 环境搭建 | ~20 分钟 |
| 第一篇论文 | ~40 分钟 |
| v2 三臂实验+写作 | ~2.5 小时 |
| v3 排版修复 | ~20 分钟 |
| v4 开放池+审计 | ~2–3 小时 |
| v5 新实验 | ~1.5 小时 |
| v6 补强轮 | ~1 小时 |
| **合计** | **约 9–11 小时** |

## 5. 成本估算

- 按 deepseek-v4-flash 官方价格估算
- 单篇论文总成本：**约 ¥10–30（$2–5）**，远低于 FARS 的 $1,040/篇

## 6. 可追溯性

- 每轮 SAR 提交 token 已存 `05_评测与迭代/提交记录_token_v*.txt`
- v5 token 明细存 `v5_token_usage.csv`
- 每实验结果存 `~/.jiuwenswarm/agent/workspace/workspace/` 下对应项目目录
- 详细流水见 `07_记录/资源日志.md`
