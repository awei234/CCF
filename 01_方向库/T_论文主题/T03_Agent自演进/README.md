# T03 Agent 自演进（论文主主题）★

> 分组：T 论文主题 ｜ 新颖度 ★★★★★ ｜ 实现门槛 高 ｜ 推荐度 ★★★★★
> 状态：主主题候选#1 ｜ 更新日期：2026-08-11

---

## 1. 主题定义

研究 Agent 如何**自主改进自身行为**（改 prompt / 工具 / rail / skill）以提升任务表现，形成"生成 → 评估 → 改进 → 再验证"的闭环。官方建议主题之一："Agent 自演进"。

## 2. 为什么选（这是创新性 25% 的主引擎）

1. **官方建议主题**，且是 Agent 领域最前沿问题（FARS 也未能解决创新性瓶颈）
2. **JiuwenSwarm 自带 Auto Harness**：Meta/Expert 双 pipeline 就是"自演进"的现成底座——实验成本被框架承担
3. **叙事闭环**：我们的系统用 Auto Harness 让 Agent 自己改进自己的科研 rail → 论文标题《Self-Evolving ...》天然有故事
4. **对应 FARS 局限 2/3**（创新性不足、机制洞察浅）——直接回答官方给的优化方向

## 3. 论文叙事模板

```
Title: Rail-Augmented Harness for Rigorous and Self-Evolving Agentic Research

Abstract 叙事：
- 问题：自动科研（FARS）两大瓶颈——实验不严谨（捏造/支撑不足）+ 系统不进化
- 方法：① 在 JiuwenSwarm Harness 层新增严谨性 rail（F02/03/04）
         ② 用 Auto Harness 让 Agent 自主改进这些 rail（自演进闭环）
- 实验：SAR 评测对比（有 rail vs 无 rail）、自演进前后的 rail 质量对比、
         与 FARS/Claude Code 基线对照
- 结论：rail 管控显著提升实验严谨性；自演进使系统持续改进；成本 $10 量级
```

## 4. 实验设计建议

| 实验 | 内容 | 对应维度 |
|---|---|---|
| E1 严谨性增益 | 有 rail vs 无 rail 的论文 SAR + 捏造率 | 实验严谨性 |
| E2 自演进闭环 | Auto Harness 改 rail 前后 SAR 对比（迭代 2-3 轮）| 创新性 + 方法 |
| E3 基线对照 | 本项目 vs FARS(5.06) vs Claude Code(5.45) vs 人类 | 重要性 |
| E4 成本 | Token/篇、时长/篇（DeepSeek $10 量级）| 应用前景 |

## 5. 风险与劣势

- **自演进实验不稳定**：Auto Harness 跑通需要环境（GitCode 认证、worktree），失败排查成本高
- 兜底：若 E2 跑不通，主题退化为"Rail 增强的严谨科研"（T04 主导），自演进作为 Future Work

## 6. 与主线的关系

- **推荐主主题**，与 D05 混合架构强绑定
- 备选主主题：T04（若时间/环境紧张，E2 用 T04 的严谨性实验替代）

## 7. 待办清单

- [ ] 跑通 Auto Harness（D04 前置）
- [ ] 完成 E1（严谨性对比实验）——阶段 3 前
- [ ] 完成 E2（自演进闭环）——阶段 5 前
- [ ] 完成 E3/E4（基线对照 + 成本）——阶段 6 前
- [ ] 撰写 Abstract/Intro 叙事草稿
