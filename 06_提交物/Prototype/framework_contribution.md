# openJiuwen 框架贡献说明

> 团队：Prototype ｜ PR：https://gitcode.com/openJiuwen/jiuwenswarm/merge_requests/4909

## 1. 代码优化点

1. **扩展 Rail 延迟注册**：`rail_manager.py` 在 inner ReActAgent 未就绪时将 rail 暂存 `_pending_rails`，就绪后自动注册，解决自定义 rail 在 chat(code) 模式不触发的问题。
2. **扩展 Rail 装配链**：`interface_code.py` 的 `_build_agent_rails` 将用户扩展 rail 正式接入 agent 装配链。
3. **科研场景工具**：新增引用核验器（OpenAlex+arXiv 双通道）、数字/声明审计工具、research-pipeline skill。

## 2. 功能拓展点

- 新增 F02 实验规划 Rail、F03 结果一致性 Rail、F04 引用核验 Rail
- 新增科研论文全流程 skill（research-pipeline）
- 新增 T3 对抗写作任务，用于制造真实伪造 headroom

## 3. PR 提交信息

- PR 名称：【科研场景拓展】修复自定义 Rail 在 chat(code) 模式不生效 + 新增科研 Rails
- PR 链接：https://gitcode.com/openJiuwen/jiuwenswarm/merge_requests/4909
- 分支：fix/rails-code-mode-assembly
- 状态：open（待合并）

## 4. 验证结果

| 验证 | 结果 |
|---|---|
| 单测 | 16/16 通过 |
| F02 集成 | 不合规 plan.json 被拦截并反馈 |
| F03 集成 | paper.tex 数字勾稽检出未验证数字 |
| F04 集成 | 引用池 17/17 verified |
| 应用验证 | v5 论文 SAR 5.8 |

## 5. 兼容性

完全兼容 JiuwenSwarm 现有版本，无破坏性变更。
