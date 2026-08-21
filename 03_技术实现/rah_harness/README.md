# RAH Harness

此目录是 RAH 的受版本控制实现；网页端生成目录不是实验或发布证据。

## 实验边界

- `experiments/sopbench_subset.json` 固定 30 条官方 SOP-Bench 测试记录、五种装配与五次重复（750 runs）。
- 真实执行必须仅通过环境变量提供 DeepSeek 密钥，并为每个 run 保存 JSONL trace 与费用记录。
- 未配置模型和 SOP-Bench checkout 时，只能运行单元测试和无加成机制模拟器；不得将模拟数据写入真实结果目录。

## 当前装配

`react`、`planner_only`、`memory_only`、`safety_only`、`rah_full`。外部工作只作为相关工作引用，绝不写成其原始实现复现。
