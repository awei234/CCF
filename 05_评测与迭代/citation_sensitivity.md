# citation_checker 敏感性分析报告（SAR 评语 3/4 回应）

> 日期：2026-08-14 · 触发：SAR 评语 3「CFR 存在性核验偏松」、评语 4「NFR 邻接启发式脆」的引用侧对应项；v2 前待办④。
> 结论先行：**发现并修复 1 个严重漏杀（捏造引用假通过），验证通过；OpenAlex 免费层限流期间自动降级 arXiv 通道，池核验不受影响。**

---

## 1. 方法

10 个边界用例 × 在线核验双通道（arXiv id / OpenAlex 标题）：

| # | 用例 | 目的 |
|---|---|---|
| c01 | 真实标题精确 | 正常通过基线 |
| c02 | 真实标题 1 词拼写错误 | 宽容度 |
| c03 | 完全捏造的 plausible 标题 | **漏杀检测（核心）** |
| c04 | 短标题（Graph Neural Networks）| 噪音误判 |
| c05 | 知名同名论文（Attention Is All You Need）| 同名歧义 |
| c06 | 特殊字符标题（引号/&）| 解析鲁棒性 |
| c07 | 标题带年份后缀 | 严格性 |
| c08 | 不存在的 arXiv id（1301.0001v2）| arXiv 拒绝 |
| c09 | 真实 arXiv id（2607.18360）| arXiv 通过 |
| c10 | 网络失败模拟 | 不误杀（ambiguous）|

## 2. 发现：c03 严重漏杀（已修复）

**旧实现**（`search={title}` 相关性检索 + 只看 top-1 的 publication_year 存在性）：
- c03 捏造标题 → **verified（假通过）**。任何 plausible 标题都能在 OpenAlex 命中部分相关结果，存在性核验形同虚设——这正是 SAR 评语 3 的技术根源。

**新实现**（2026-08-14 v2 修复，`03_技术实现/tools/citation_checker.py`）：
1. `filter=title.search:"{title}"` 短语搜索（标题必须整体出现）
2. top-1 标题规范化（小写/去标点）+ `difflib` 相似度阈值：≥0.92 verified / ≥0.60 ambiguous / <0.60 not_found
3. 429/5xx 退避（429 只重试 1 次，IP 级限流重试无意义）
4. 双通道取并集证据：arXiv id 优先（强证据、API 稳定）→ OpenAlex 标题兜底；任一 verified = verified，全 not_found = not_found，其余 ambiguous

## 3. 修复后验证

**本地网络 OpenAlex（本机 IP 未限流）**：

| 用例 | 结果 | 判定 |
|---|---|---|
| c01 真实标题 | verified | ✅ 精确命中 |
| c02 拼写错误 | not_found | ⚠️ 过严（短语搜索 1 词差异不中；池场景 arXiv id 兜底不受影响，可接受）|
| c03 捏造标题 | **not_found** | ✅✅ **漏杀修复验证成功** |
| c04 短标题 | ambiguous | ✅ 不误杀 |
| c05 知名同名 | verified | ✅ 真实存在（作者/版本歧义属 support alignment 层，见 §5）|
| c06 特殊字符 | not_found | ✅（OpenAlex 未命中该标题；短语搜索对标点处理稳健）|
| c07 年份后缀 | not_found | ⚠️ 过严（OpenAlex 标题不带年份；池场景标题来自 meta_info 无后缀，不受影响）|

**服务器双通道 verify_pool（references 池 17 篇）**：**17/17 verified**，0 not_found / 0 ambiguous——arXiv id 通道独立完成全池核验，OpenAlex 429 期间无影响。

**限流行为**：OpenAlex IP 级 429 期间，OpenAlex 通道全部返回 ambiguous（不误杀设计生效），由 arXiv 通道兜底；c08 不存在 id → not_found、c09 真实 id → verified、c10 网络失败 → ambiguous，全部符合预期。

## 4. 结论

- ✅ 存在性核验的漏杀通道已堵死（c03 假通过 → not_found）
- ✅ 双通道冗余：任一通道不可用不阻塞核验
- ✅ 不误杀原则保持（ambiguous 只提示不阻断）
- ⚠️ 2 个过严点（c02/c07）在池场景无影响，不调整（调整会牺牲防漏杀强度）

## 5. 剩余局限（v3/阶段 3 建议，不在本轮范围）

1. **support alignment（语义错配）**：引用存在但内容不支撑论断——SAR 评语 3 的另一半，F04 只验存在性，需人工/LLM 抽样复核（E1 支持率指标）
2. **同名歧义**（c05）：存在性通过但无法确认"这篇"——需作者/年份联合校验（OpenAlex 返回含 authors，可加）
3. **Crossref 第三通道**：SAR 评语 3 点名"多源（CrossRef）"——当前 arXiv+OpenAlex 已双源，非 arXiv 文献（会议/期刊）建议 v3 补 Crossref
4. **OpenAlex 免费层限流**：共享池，无 Retry-After；长轮询任务建议错峰（0.6s+ 限速 + 退避已内嵌）

## 6. 关联文件

- `03_技术实现/tools/citation_checker.py`（修复后，已同步服务器）
- 服务器 `tools/sens_citation_checker.py` + `sens_citation_report.json`（10 用例原始输出）
- 本地 `.zcode/tools/local_openalex_check.py`（本机验证脚本）
