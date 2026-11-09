# KB Batch63｜课标上下文原子拆分假设、12篇数学风险讲义与精确验证

执行日期：2026-11-09。开发、内容生产、源码检查和测试仅在授权 MacBook Air（Darwin）独立 worktree 完成。未使用 Tang，未修改 Mac 主仓原有11处未提交变更，未合并 main、未强制推送。

## 基线和关联任务

- 代码基线：Draft PR #87、Batch62 HEAD 57239d28326b906078ddedfaacdbccdb2800d773。
- 本批源码提交：1e3810923b0ad7c3f2d55e300a4fadca66abad00；最终报告/日志提交以本分支后续 HEAD 为准。
- 任务：#17 Master；#18 K00；#19 K01；#20/#21/#22/#23 内容分域；#24 K06；#25 K07；#26 K08；#27 K09。
- 截至本次读取，#17–#27 全部为 Open；最近交付 #87 为 Draft。不能据此声称项目或任一课程轨道完成。

## K00：原版课标来源的45处窗口和62处原创拆分假设

- 本机读取锁定 PDFKit 来源；对31处有数学实质的锚点以及14处非知识原子的学业/教学/栏目锚点，构建45个带页、行区间、页SHA、行SHA、窗口SHA的审查窗口。
- 本机用脚本的 --verify-local --check 直接重新比较45处窗口与原版PDFKit文字指纹（PASS）；CI只能审核锁定的版本化快照，不能代替Mac版权原件复核。
- 每个数学实质锚点提出两项不同方向的编辑拆分假设，共62项，作为未来课程原子化的起始队列；这些**不是**正式官方课程知识原子、不是62篇完整讲义，也不是覆盖率分母。
- 14项学业/教学/栏目要求继续独立 UNMAPPED，不因不能转化为一个数学概念而从能力覆盖审计中消失。
- 印刷第35页数学建模流程图尚需视觉/教师复核；无法证明窗口覆盖完整条款或解决跨页数学等价。
- 上述结果版本化在 curriculum/highschool_math/k00_batch63_context_windows.json、k00_batch63_provisional_atom_proposals.json 和 docs/evaluation/KB_BATCH63_ATOM_SPLIT_AND_SOURCE_WINDOWS.md。原版课标全文及版权PDF均未上传。

## K01 / K06：12篇原创教师侧风险讲义

新增 knowledge/editorial_review/kb_batch63_risk_conditions.json，配套可重算审核矩阵与摘要。12个主题：
不等式负数乘法；量词否定；二次不等式判号；有理指数定义域；三角恒等变形除数；二分法存在性/唯一性；平面向量基底；SSA多解；复数除法非零；空间投影伪相交；非均匀有限概率；微分与真实增量。

每篇包含适用假设、符号、先修、至少三步有理由的推演、两个教师例题、错误推导根源、反例、三层启发提示及近/远迁移。合计教师例题24、理由步骤36、反例12、提示36。自动检查验证结构和状态字段，不是教育专家对数学内容的批准。

全部采用 REVIEW_PENDING、TEACHER_ONLY、NOT_FORMALLY_CERTIFIED、student_publishable=false；未将其加入正式学生RAG索引，也未伪造教师签章、学生解题认证或课标等价结论。12篇不是12条正式官方覆盖成果。

## K07：12类有限精确数学见证及本轮修复

- 在 backend/app/kb_batch63_exact_checks.py 中加入不等式负乘、有限论域量词、两异根二次函数符号、约分有理指数实数域、三角商式、一次二分、二维基底唯一系数、30度SSA分支、复数共轭除法、空间异面直线、非等可能事件概率、微分与真实增量的12类受控算例。
- 检查结果只适用于明确的整数/Fraction/SymPy有界对象，标签 FINITE_EXACT_CASE_ONLY。绝不推断一般定理的形式证明或验证学生自由作答。
- 独立复核时识别两个实际安全缺口并修复：事件列表允许重复结果时会把同一基本事件概率重复计数；符号角余弦是否非零不明时，单靠表达式不等于零可能被误当作合法除式。新增拒绝重复事件、非法质量类型、非闭式符号角或浮点角的负面测试。
- 合法前提失败必须抛 FailedPremise；不满足假设的表达式不能默认断言成立。

## K08：学生检索门禁（离线）

测试复用已有**非空批准内容集合**的测试专用签名fixture，执行 student_evidence_lookup。12篇新教师草案未出现在正式学生知识仓或召回结果，教师完整解答没有暴露；本次没有请求实际生产LLM API。这是离线单元/集成安全回归，不可替代冻结的真实API对照评测。

## K09：Mac实际执行和失败留痕

| 检查 | 实际结果 |
| --- | --- |
| Batch63专项，最后一次修复后 | 221 passed、0 failed |
| Python后端全量（含上述221） | 45,300 passed、0 failed、1第三方弃用警告 |
| Node.js测试 | 111/111 passed |
| Tutor离线策略 | 33/33 |
| RAG困难负例 / Top3 | 40/40、22/22 |
| Chrome/Playwright及browser pytest | 15个脚本 + 2个pytest，最终浏览器日志/退出码见下 |
| scripts/mac_check.sh | EXIT 0 |
| scripts/mac_browser_check.sh | 最终退出码见下 |

测试日志保留在 evaluations/results/2026-11-09-kb-batch63/，含独立增量、全量、浏览器日志以及exit文件。原始一次增量测试出现212 passed / 1 fixture setup error：外部fixture未显式导入，随后修复，增量测试通过；原始错误在 incremental_initial_failed.log。后续增加数学边界负例时，一项测试误将 0.5 与 Fraction(1,2) 的数值相等当成类型相同，触发220 passed / 1 failed；改用类型全等判定后221 passed。该次覆盖写入最终专项日志，故失败示例在本报告中独立记录。旧评测文件的生成时间戳被完整检查暂时更新，已在独立worktree恢复基线，避免把无关fixture漂移提交。

Mac浏览器以合成数据和CDP模拟，不是实体iPad/学生真实学习成效证明。无真实学生数据、无版权课标全文、无外部LLM调用。

## 未完成事项与下一批

- 官方课标必修、选择性必修、选修A–E七轨独立知识原子分母全部仍为 null；61/61页“有部分来源线索”不代表完整人工原子化，逐页教师完整审查仍为0/61。
- 428条旧候选锚点、344条非去重旧来源指针及本批62拆分假设均不得合计为课程知识原子覆盖数量。12份稿件仍未教师签字。
- 538条历史证明步骤未形式认证，10组数学冲突未正式裁决；真实教师批准=0，学生端正式深度发布=0。
- 下一批：对31项来源锚点继续核对整条课标上下文、跨页引用和未编号要求；对14项能力要求逐项关联可测试的题族/教学行为；对第35页嵌图补视觉证据；对12篇风险稿开展数学等价审校和教师审查，同时扩大其他课程领域完整内容覆盖；继续定理前提证明、反例的严格机器与人工分工。
- 在真实教师审核及正式全量分母完成前，保持 Draft PR、#17–#27开放及自动续建任务。

## 附：校验命令

在 Mac 独立worktree运行：

    .venv/bin/python scripts/build_kb_batch63_atom_context.py --check --verify-local
    .venv/bin/python scripts/validate_kb_batch63_risk_lessons.py --check
    PYTHONPATH=backend .venv/bin/python -m pytest -q backend/tests/test_kb_batch63_atom_context_lessons.py
    ./scripts/mac_check.sh
    ./scripts/mac_browser_check.sh

mac_check.log SHA256: f3d0df3dc8b7f850cc78c256809c7b5df7de49235ade578a09579adc4834053b
mac_browser.log SHA256: 49d3e25b9fe11b045ffb2ea8825abc5110b82f88f5300889a71f1f7d44162597
mac_check.exit: 0
mac_browser.exit: 0

