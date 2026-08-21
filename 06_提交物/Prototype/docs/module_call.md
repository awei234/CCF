# openJiuwen / JiuwenSwarm 模块调用说明

本项目基于 JiuwenSwarm 开发，核心模块调用如下：

## 1. 基础调度与生命周期

- `jiuwenswarm-start app`：启动 JiuwenSwarm 服务
- `jiuwenswarm chat`：启动 Agent 会话，触发 skill 与 rails

## 2. Skill 机制

- `research-pipeline` skill 随技术包位于 `code/custom_skills/research-pipeline/`
- 通过 SKILL.md 的 description 触发

## 3. Rail 扩展机制

- 继承 `openjiuwen.harness.rails.DeepAgentRail`
- 实现 `before_tool_call` / `after_tool_call` / `after_task_iteration` 钩子
- 通过技术包内 `code/extensions_config.json` 提供的配置启用；安装目标目录由部署环境决定
- 本项目修改了 JiuwenSwarm 源码 2 个文件共 32 行：
  - `agents/harness/common/plugins/rail_manager.py`：扩展 rail 延迟注册
  - `server/runtime/agent_adapter/interface_code.py`：扩展 rail 接入正式装配链

## 4. 工具调用

- `tools/citation_checker.py`：调用 OpenAlex / arXiv API
- `tools/verify_api.py`：核对 rail API 签名

## 5. 数据契约

- `plan.json` → `experiments/*/results.json` → `paper/paper.tex` 逐级勾稽
- `code/demo/` 是无密钥工程演示，所有报告均带 `demo_only` 标记；它不构成 v6/v7 实验数据。
