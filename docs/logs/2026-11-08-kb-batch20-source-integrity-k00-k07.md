# STEM Mentor KB Batch20 — K00/K01/K07/K09 来源真实性、分段函数边界与可审计待审核队列

**执行环境**：授权的 MacBook Air；独立 worktree `stem-mentor-kb-batch20`，分支 `feat/kb-batch20-integrity-and-coverage`。基础为 [Draft PR #45](https://github.com/YOUessi/stem-mentor/pull/45) GitHub commit `fe4ff575ad445e5bc65dbca8ba9f3cca6783116a`。无 Tang 开发；不接触 Mac 主仓 11 项原有未提交改动，也不更改 Batch18/19 其他 worktree，绝不自动合并 main。

## 本批事实边界

- 本批新增深度教学知识单元：**0**。本批处理的是课标基础事实完整性/发布可信度的 P0 验证缺陷，而不是把审计任务计入“新增讲义”。
- 既有 **224 篇 REVIEW_PENDING 结构化草案**并未获得教师审核；历史的 **451 个 NOT_FORMALLY_VERIFIED 自然语言证明步骤**依旧未被整体认证。P0=127、P1=118、P2=206 是风险排序，不是通过/失败量。
- 教师实签批准 0、学生深度知识正式放行 0。**10/10 冲突仍待教师独立裁决，23 项历史语义缺口和 28 项课程编辑缺口均 OPEN**。
- 课标全量原子知识分母、每个 track 的官方全量知识原子完成率仍为 **null**，无论有多少 marker/页面、人工编辑目标或代码测试通过，都不能用这些数替代。

## 修复 1｜冻结来源 SHA，而不是只检查 64 位十六进制格式

原先 `validate_ledger` 对源 PDF SHA、页 SHA、行 SHA 只做格式校验；`ffffffff...` 这种格式合法、内容伪造的摘要可能在通过其它一致性检查时放行。现在：

1. **固定上一批经 Mac 重抽取验证的 PDF SHA256**：`cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。它与官方来源 URL 构成基础源标识。
2. 对现有来源账本的全部字段（源码源信息、61 页的页哈希、315 条编号标记/行哈希、分轨计数、未审核状态和分母契约）进行规范化 JSON SHA256，一次性与**独立固定的抽取快照摘要** `26abbb442d8ebf4c7866af11475a139235efb004d452fe1080c4238996dac53b` 比对。
3. 新增 10 类篡改负面回归，含**格式合法的 PDF/页/行哈希伪造**、行哈希交换、页方向/标题/说明变化。发生来源证据变化时必须重新核实源 PDF 与显式更新可信快照，不能静默当成原来的课标。
4. 这是**版本冻结/偏移监测**，不是课标准确性保证、加密签章、第三方签名或教师签审；源 PDF 原文仍不提交到仓库。

涉及 `backend/app/official_clause_audit.py`、`backend/tests/test_kb_batch20_source_guard_queue.py`。

## 修复 2｜不再将 x/x 错称为 x

旧 K07 32 项有限子命题检查中一条写“分段 x/x 在 0 未被迫不连续”，实际计算的是 `x`。新检查区分：

\[
r(x)=x/x,\quad D_r=\mathbb R\setminus\{0\},\quad r(x)=1\ (x\ne0).
\]

`r(0)` 未定义，不能直接谈原函数在 0 连续。若人为补点 `f(0)=1`，则得到连续延拓；若补 `f(0)=0`，则函数在 0 不连续。对所有非零有限整数域点以精确分数验证 `r(x)=1`，对 `0/0` 必须抛出 `ZeroDivisionError`；使用 SymPy 极限核实延拓条件。新增**一条独立有限子命题检查**，从 32 → 33；10 对版本冲突**仍未裁决**。已重建 `KB_BATCH18_SOURCE_AND_PROOF_RISK_AUDIT.json`，保持历史 451 风险队列字段结构与统计不变。

涉及 `backend/app/batch18_math_checks.py`、`scripts/build_kb_batch18_proof_risks.py`、相关冻结审计及测试。

## K00/K01/K09｜真正可审计的课标分轨人工待审任务

新增确定性生成器 `scripts/build_kb_batch20_k00_review_queue.py`、冻结矩阵 `docs/evaluation/KB_BATCH20_K00_REVIEW_QUEUE.json`、安全汇总 `backend/app/k00_review_queue.py`、新增 `/api/knowledge/standard-progress` 的非敏感 `k00_human_review_worklist` 字段、CI `--check` 门禁。

**共有 427 项需要人工判定的工作任务，绝对不是 427 个知识原子**，它们可能跨类别重叠：独立页面需要拆分 61；编号位置需验证和原子化 315；选修 D/E 已定位未编号标题需拆分 23（D=17、E=6）；编辑缺口候选待确定是否真正缺课 28。原有 132 项编辑目标候选以单独指标报告，未转换成已经完成的课程。

7 条课程方向单列：必修、选择性必修、选修 A/B/C/D/E。每轨保留来源页、编号位置、D/E 未编号条目、项目编辑目标、待判缺口、独立未审校字段，并明确 `official_atomic_denominator=null`、`official_coverage_rate=null`、`approved=0`。选修 E 是学校选择的拓展例子，不能被夸大为全国普遍必修内容。工作单具有来源页 SHA、关联 ID、类型及 `HUMAN_CURRICULUM_AND_MATH_REVIEW_PENDING`、`student_publishable=false`，并且所有字段必须可由冻结证据重新生成；伪造批准/覆盖率/来源页会被拒绝。

**注意不同 Batch18 PR 的两套来源抽取方法**：#44 使用 248 个标记候选，#45 使用 315 个标记候选，其抽取方式与匹配范围不同。这一批基于 #45，未合并 #44、未将 248+315 相加，也未抢占 Mac `stem-mentor-kb-batch19` 中尚未提交的双源校对工作。后续应独立核对两者差异，再复核未编号要求和原子分母。

## 数学安全验收

针对新增来源完整性、冻结审查任务、分段定义域、零分母、分段补点连续性与超几何条件做参数化负例检查；保持 `REVIEW_PENDING`、`TEACHER_ONLY`、Approved-only 学生知识检索门禁，不把有限精确代数检验当作完整证明。

### Mac 实际执行

以下为执行命令，详见同目录的版本化测试日志：

- `PYTHONPATH=backend .venv/bin/python -m pytest backend/tests/test_kb_batch20_source_guard_queue.py backend/tests/test_kb_batch18_source_math.py -q`：**2,846 passed，0 skipped（本批新文件 2,128 参数化通过 + 历史来源数学专项 718）**（详见 `python-targeted.log`）。
- `PYTHONPATH=backend .venv/bin/python -m pytest backend/tests -q`：**14,397 passed，1 warning（第三方依赖），0 failed；6 分 18 秒**，日志 `python-full.log`。
- `node --test tests/node/*.test.cjs`：**111 passed**，详见 `node.log`。
- `python scripts/audit_kb_batch18_source_proofs.py --check` 与 `python scripts/build_kb_batch20_k00_review_queue.py --check`：已通过；**30/30 Python CI 脚本门禁 PASS**，详见 `ci-python-gates.log`。
- `cd backend && PYTHONPATH=. .venv/bin/python evaluate_policy.py`：**33/33** 合成教学策略与检索决策通过；`evaluate_v05.py`：**40/40** 硬负例检索通过（top3 22/22）。
- `bash scripts/mac_browser_check.sh`：Mac Chrome 本地临时数据库/动态端口的浏览器回归，最终结果见 `browser.log`。浏览器指针模拟不等于 Apple Pencil 真机验收。

**修复过程中的失败**：首次使用 macOS 系统 `/usr/bin/python3` 重建证明冻结报告，因环境无 SymPy 报 `ModuleNotFoundError`，随后显式使用 Mac 项目已存在的隔离 Python venv 重新运行并成功；不属于数学算法失败。原工作树只有 .venv 只读复用链接，未复制或修改其它项目代码。

本批所有脚本运行路径均为 Mac 授权 worktree；最终 GitHub commit/tree SHA 与远端 CI 以本报告对应 Draft PR 的实际对象为准。

## 下一批必须继续

1. **K00 + K01**：和 Batch18 #44、#45 独立来源方法逐页对账，确认尤其选修 A p56–57、选择性必修 p40 的遗漏；分解所有未编号要求，形成经过人类审核的必修/选必/选修独立原子分母，不采用 427 工作任务或 315 标记冒充原子数。
2. **K02–K05 + K06**：对真缺课项扩增原创内容，并逐条补定义、假设、可复核分步推理、边界、反例、两道例题、错解、三级提示、近远迁移，教师侧解答不得泄漏。
3. **K07**：优先逐项检查 127 条高风险证明步骤的前提/有效性，10 对历史争议版本由真正教师决定；保持未形式认证状态而不是让模型打分签审。
4. **K08 + K09**：索引/检索发布隔离、API 回归/错误拒答和版本撤销测试，只有独立教师签名链闭环后才允许 APPROVED 的学生端知识发布。
