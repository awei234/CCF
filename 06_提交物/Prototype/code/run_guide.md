# Prototype 复现指南

> 本技术包提供两级复现：**离线 demo 审计**无需模型密钥或服务器；**真实 Agent/实验**需要另行配置 JiuwenSwarm、模型与实验脚本。demo 数据仅用于验证工程链路，不是 v6/v7 的实验结论。

## 1. 环境准备

- Linux 或 WSL，Python `>=3.11,<3.14`。
- 创建隔离环境并安装依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- 如需真实模型运行，复制 `config.example.yaml` 为本地 `config.yaml`，仅通过环境变量提供模型密钥。

## 2. 无密钥 demo 复现（推荐先运行）

在 `code/` 目录执行：

```bash
python bootstrap.py --check --demo-audit --output /tmp/demo-audit.json
# 或使用统一入口
python main.py --stage demo-audit --audit-output /tmp/demo-audit.json
```

预期结果：命令返回 `0`，并生成标有 `demo_only: true` 的审计报告。该检查验证扩展配置、F02/F03/F04 源文件、科研 Skill、演示计划、结果、论文数字与引用池之间的离线一致性。

## 3. 启动真实 JiuwenSwarm 服务（可选）

```bash
# 进入你的 JiuwenSwarm venv
source /path/to/jiuwenswarm/.venv/bin/activate
nohup jiuwenswarm-start app > service.log 2>&1 &
# 等待端口 19001 可访问
```

## 4. 启用自定义 Rails（真实运行）

技术包已附带 `extensions_config.json`。将 `code/custom_rails/` 和该配置文件安装到 JiuwenSwarm 的扩展目录后启用；具体目标目录随已验证的框架版本而定，禁止依赖作者机器的绝对路径。

```json
{
  "experiment_planning_rail": {"enabled": true, "class_name": "ExperimentPlanningRail", "priority": 50},
  "result_consistency_rail": {"enabled": true, "class_name": "ResultConsistencyRail", "priority": 45},
  "citation_verification_rail": {"enabled": true, "class_name": "CitationVerificationRail", "priority": 40}
}
```

## 5. 运行科研流水线（需要模型配置）

```bash
python main.py --stage skill
```

## 6. 复现论文实验（后续阶段）

真实 v6/v7 实验需要导入对应的 `plan.json`、逐 seed `results.json`、模型配置与预注册协议。若 `experiment_script` 未配置，下面命令会以非零退出，避免误判为复现成功：

```bash
python main.py --stage experiment
```

## 7. 生成论文与提交 SAR

- 使用 `code/custom_skills/research-pipeline/` 的 Writing 阶段生成 `paper/paper.tex`；
- 编译为 PDF：`pdflatex paper.tex`；
- 到 https://paperreview.ai 上传 PDF（Venue=ICLR），保存返回的 token。
