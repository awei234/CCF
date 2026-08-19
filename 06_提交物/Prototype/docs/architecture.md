# Prototype 架构设计文档

## 1. 整体架构

基于 JiuwenSwarm 的科研论文自动生成系统，采用“科研流水线 Skill + 进程级验证 Rails + 审计闭环”的架构：

1. **接入层**：用户输入选题或任务（T1 规划 / T2 写作 / T3 对抗写作）
2. **流水线层**：`research-pipeline` skill 驱动 Ideation → Planning → Experiment → Writing
3. **管控层**：自定义 Rails
   - F02 实验规划 Rail：强制 plan.json 满足实验严谨性契约
   - F03 结果一致性 Rail：检测论文数字是否可追溯到 results.json，并提示修复
   - F04 引用核验 Rail：检测引用是否命中本地池，并提示在线核验
4. **审计层**：CFR/NFR/UCR 指标计算 + 人工/规则审计 + 独立审计
5. **输出层**：paper.tex → PDF → SAR 提交

## 2. 模块拆解

- `custom_skills/research-pipeline/`：科研全流程 skill（prompts + workspace schema）
- `custom_rails/`：F02/F03/F04 rail 实现与单测
- `custom_rails/utils.py`：JSON 加载、数字提取、工作区路径解析等共享工具
- `tools/citation_checker.py`：OpenAlex + arXiv 双通道引用核验
- `tools/verify_api.py`：Rail API 签名核对

## 3. 数据流

```
用户任务 → research-pipeline skill
  → proposal.md / idea.json / references/
  → plan.json（F02 校验）
  → experiments/*/results.json（F03 勾稽）
  → paper/paper.tex（F03/F04 校验）
  → PDF → SAR 提交
```

## 4. 关键设计决策

- **Measurement is auditing**：CFR/NFR/UCR 与 rail 检查同构，使测量本身成为审计。
- **Paired seeds**：所有臂共用 seed 42/43/44，形成同 seed 配对比较。
- **Adversarial T3**：禁用在线核验，制造真实伪造 headroom，避免地板效应。
- **两级复现**：离线 demo 仅验证包布局与审计数据链；真实模型实验需单独导入数据与配置，二者不得混用。
- **门控边界**：F02 在写入计划前执行硬拦截；F03/F04 当前为 detect-and-repair，不应表述为实时强制阻断。
