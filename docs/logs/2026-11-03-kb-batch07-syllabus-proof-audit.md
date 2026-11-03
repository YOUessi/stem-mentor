# STEM Mentor｜Batch07 深度知识增补、选修范围与证明义务门禁

日期：2026-11-03（Mac 开发批次）
基线：Batch06 commit `930d9e7f2e1a288b7f035c8776f6d194032873dd`。
分支：`feat/kb-batch07-syllabus-proof-audit`，叠加 PR #32。GitHub PR/CI 结果须以远端状态确认。

## 真实交付

1. **新增 8 篇项目原创定理型教研草案**，每篇含：原命题与全部使用条件、3 条有独立依据的证明步骤、反例/失效边界、常见误区与纠偏问法、2 道教师侧例题、3 层提示、近远迁移、来源与 REVIEW_PENDING 状态。数学主题：集合德摩根律、严格单调函数反函数、等差通项与归纳、乘积求导、圆的弦长与相切、方差仿射变换、分割事件贝叶斯公式、两集合容斥。源文件由 `scripts/build_kb_batch07_lessons.py` 决定性生成，不是复制教材全文。
2. **现在累计 146 篇深度草案**：theorem=66、concept=66、method=14；无一正式教师审核通过，未通过完整自然语言形式证明。原始 113 条课程索引仍仅为项目工程条目，不是官方全部原子教材。
3. **A–E 选修高层覆盖矩阵**：从既有 `official_scope_v1.json` 中逐项提取五方向共 18 个高层主题槽位，并将原有 7 个「选修拓展」工程条目标记为 `ELECTIVE_TRACK_NOT_ASSIGNED`。**官方课程原子课程映射审核=0**，高层主题不能冒充逐课标完整覆盖。
4. **10 个历史重名知识冲突独立审查队列**：保存两版 SHA256、冲突假设、适用边界和反例，以及每项的专属数学风险核对问题。没有自动覆盖/伪造裁决，保持 `HOLD_BOTH_SOURCE_VERSIONS`。
5. **146 篇逐条数学证明义务清单**：66 篇定理共 214 条步骤仍标为 `NOT_FORMALLY_VERIFIED`，48 条既有 K07 子命题数学检验仅作为有限证据引用，不声称证明完整性。
6. **修复编辑态 RAG 截断缺陷**：原先 FTS 排名前 100 再按 curriculum/kind 过滤，会遗漏超过第 100 位的合法匹配。现改为在本地小语料中先保留全部命中再过滤，并用合成 140 篇查询验证尾部相关文档可找回。学生端仍仅返回 `NO_APPROVED_EVIDENCE`，没有未经审批的教师证明和解题过程泄露。
7. **历史可复现性修复**：冻结 Batch02→Batch06 39→29+10 的冲突基线，避免 Batch07 新增独立内容导致旧报告漂移；新增 Batch07 的语义覆盖审计快照，保留 Batch06 原始快照不覆盖。

## 实际数学验证与边界

- 10 类历史冲突知识各采用 11 个有限、精确、独立的数学输入，共 **110 个参数化核对案例**，涵盖复合函数定义域、奇偶性、分段点、介值定理、点线距离、二项与超几何概率、回归斜率、三角形面积、向量分配律。
- 新增 8 篇草案各 **2 道受控例题共 16 个**独立符号/集合/有理数验算，另外对典型负例建立回归断言。
- 这些结果**不是 214 条完整证明已认证**；尤其“相关不等于因果”的推断是统计解释，不能靠一条符号恒等式验证。
- 所有内容仍是 `REVIEW_PENDING / TEACHER_ONLY`；自动 Schema 校验、例题数学验算和浏览器回归均不能代表正式教师审核。

## 验收命令

```bash
cd ~/Documents/文件/stem-mentor-kb-batch07
.venv/bin/python scripts/build_kb_batch07_lessons.py --check
.venv/bin/python scripts/build_kb_batch07_audit.py --check
.venv/bin/python scripts/reconcile_kb_batch02.py --check
.venv/bin/python scripts/audit_kb_semantic_coverage.py --check
(cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q)
node --test tests/node/*.test.cjs
bash scripts/mac_browser_check.sh
```

**修复后 Mac 验收：Python 1315 passed（1 条环境弃用警告）、Node 111/111、教学策略 33/33、检索负例 40/40，完整 Chrome 浏览器回归已 PASS（含 v0.5–v0.14 历史浏览器流程、2 条 pytest 浏览器审查）；仅合成数据，iPad 并非真机 Apple Pencil 验证。** 本批首次全量尝试发现 2 个历史快照漂移测试失败（1313 passed、2 failed），已修复：旧冲突基线冻结、语义覆盖使用 Batch07 新快照，并进行了局部回归复验。正式最终全量数字在 PR 验收记录中更新；不要把首次有失败的测试报告称为成功。

## 还未完成的硬门槛

- 必修/选择性必修**官方课标逐原子**人工映射仍未通过；所有选修 A–E 目前仅有高层主题槽位，没有逐项正式核对。
- 10 项旧版冲突尚未独立数学裁决，不能发布自动合并的知识。
- 214 条当前定理证明步骤未获形式证明或真实教师审定；23 个历史语义缺口仍 OPEN。
- 学生知识驱动 Agent 仍未在正式审核后端到端发布，任何 API 调用都不能直接把未审内容视为数学权威。

## 下一批链路建议

先有证据地整理选修 A–E 中各方向官方子项及地区/年份差异→为每个子项增建真正知识原子 ID 而不是按高层主题凑数→对十项冲突逐条独立数学判定并出复核记录→建设支持真实教师签名审核和撤回机制的 Approved-only RAG→再进行真实 API 教学评测与学生无提示迁移测试。不得将审批模拟、模型判断或格式检查冒充人工签核。
