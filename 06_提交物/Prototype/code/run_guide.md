# Prototype 复现指南

## 1. 环境准备

- Linux 服务器，Python >= 3.10
- 安装依赖：

```bash
pip install -r requirements.txt
```

- 按 `config.yaml` 配置模型 API、JiuwenSwarm 路径、工作区路径。

## 2. 启动 JiuwenSwarm 服务

```bash
# 进入你的 JiuwenSwarm venv
source /path/to/jiuwenswarm/.venv/bin/activate
nohup jiuwenswarm-start app > service.log 2>&1 &
# 等待端口 19001 可访问
```

## 3. 启用自定义 Rails

将 `code/custom_rails/` 下的 F02/F03/F04 复制到 JiuwenSwarm 扩展目录，并在 `extensions_config.json` 中启用：

```json
{
  "experiment_planning_rail": {"enabled": true, "class_name": "ExperimentPlanningRail", "priority": 50},
  "result_consistency_rail": {"enabled": true, "class_name": "ResultConsistencyRail", "priority": 45},
  "citation_verification_rail": {"enabled": true, "class_name": "CitationVerificationRail", "priority": 40}
}
```

## 4. 运行科研流水线

```bash
python main.py --stage skill
```

## 5. 复现论文实验

服务器端已提供批处理脚本：

```bash
bash /data/vergil-CCF/scripts/run_v5_experiments.sh
```

或在本地按论文 `Experiments` 一节逐臂运行：

```bash
python main.py --stage experiment
```

## 6. 生成论文与提交 SAR

- 使用 `code/custom_skills/research-pipeline/` 的 Writing 阶段生成 `paper/paper.tex`；
- 编译为 PDF：`pdflatex paper.tex`；
- 到 https://paperreview.ai 上传 PDF（Venue=ICLR），保存返回的 token。
