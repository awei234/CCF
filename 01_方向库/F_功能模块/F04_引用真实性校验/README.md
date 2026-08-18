# F04 引用真实性校验 Rail（第一批核心）★

> 分组：F 功能模块 ｜ 实现成本 低 ｜ 影响维度：相关工作完整性 10% + 防捏造
> 状态：阶段 2 开发 ｜ 更新日期：2026-08-11

---

## 1. 模块定义

一个自定义 rail（或写作阶段工具），在**引用落笔前/后**在线核验每篇参考文献的真实存在性，杜绝"假引用"（Codex 8% vs Kimi 72% 的差距维度）。

**一句话**：论文引用的每一篇文献，都要在线查得到。

## 2. 为什么是第一批

- 假引用直接摧毁"相关工作完整性"维度（10%）和整体可信度
- 实现成本最低、收益直接（调用公开 API 即可）
- 引用核验还能反向约束写作质量（逼 agent 真读文献）

## 3. 功能规格

### 3.1 核验渠道

| 渠道 | 用途 | 说明 |
|---|---|---|
| arXiv API | 论文类引用核验 | `http://export.arxiv.org/api/query?id_list=...`（免费）|
| Semantic Scholar API | 通用引用核验 | `https://api.semanticscholar.org/graph/v1/paper/search`（免费额度）|
| CrossRef API | DOI 核验 | 免费 |

### 3.2 校验规则

| 校验项 | 规则 |
|---|---|
| 存在性 | 引用条目（标题/作者/年份）能命中在线库 |
| 一致性 | 引用标题与论文正文表述一致（防"张冠李戴"）|
| 时效性 | 相关工作必须覆盖新 baseline（FARS 通病：拿旧 baseline 对比）|
| 数量 | 短论文合理引用量（建议 25-40 篇，视模板）|

### 3.3 失败动作

- 写作 rail 拦截：列出"未验证引用清单"，引导 agent 替换为真实文献
- 给 agent 提供"引用候选池"（调研阶段先建立，写作阶段只许从池里取）

## 4. 实现要点

```python
class CitationVerificationRail(DeepAgentRailBase):
    priority = 800
    def after_model_call(self, ctx):
        cites = extract_citations(ctx.output)
        bad = [c for c in cites if not verify_online(c)]   # arXiv/S2 API
        if bad:
            return citation_fix_guide(bad)   # 引导替换
```

> 注意：网络调用放 rail 里可能拖慢节奏 → 可设计为**异步/批处理**，或放在写作阶段单独工具，rail 只做"引文格式与来源标记"检查、在线核验由工具完成。

## 5. 挂载方式

- rail：`03_技术实现/jiuwenswarm/jiuwenswarm/agents/harness/code/rails/citation_verification_rail.py`
- 配套工具：`tools/citation_checker.py`（批量核验脚本，可独立于 rail 用）

## 6. 验收标准

- [ ] 假引用 100% 被拦（在线核验命中率测试）
- [ ] 真实引用无误伤（白名单/容错机制）
- [ ] 相关工作章节引用了近 1-2 年的新 baseline

## 7. 参考依据

- FARS 评测论文 §5.2（假引用数据）+ §5.1（引用幻觉相关）
- arXiv API / Semantic Scholar API 文档
- FARS 附录 B Writing 指南（引用合规要求）

## 8. 待办清单

- [ ] 实现 citation_checker.py（arXiv + Semantic Scholar 双通道）
- [ ] 实现 rail 校验逻辑 + 修正引导
- [ ] 容错设计（网络失败不误伤真实引用）
- [ ] 单测（真实/伪造/模糊引用场景）
- [ ] 挂载进写作阶段
