# STEM Mentor｜Batch57 执行与验收记录（2026-11-09）

## 源码、环境和真实工作边界

- **唯一代码与内容开发/测试设备**：已授权 MacBook Air；独立 worktree ~/Documents/文件/stem-mentor-kb-batch57，分支 feat/kb-batch57-source-geometry-probability。
- 基线：Batch56 Draft PR #81 的已验收 GitHub SHA 8227bd5f385a1a116cc93af55979d06ce20cd167。Mac主仓原11项未提交修改没有变更；没有使用 Tang、合并或重写 main。
- **本批真实源码提交 SHA**：a8d8c37f906c52b1ae9f7ddb927afea25a42a698；其 Git Tree：09ac3cc503de07ac1e5ad622474f0155700a3bc9。
- 官方课标PDF的锁定 SHA256：cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195。原文件及其逐页抽取文字仅驻留本机/private/tmp，**没有上传到 GitHub**。
- 本报告的第二个文档提交、GitHub Draft PR 与 Actions 状态需以远端实时检查为准。本地测试通过不代表GitHub CI已经通过。

## 先检查11个GitHub Issues / 上游 PR

2026-11-09实时读取#17及#18–#27：全部仍为Open。上游最新PR #81为Open、Draft、Mergeable，Head为8227bd5；Batch56已完成15–24页52条来源定位。重要依赖：K00官方原子分母仍缺失，K07历史538证明步骤尚未形式认证与10冲突未裁决，K08/K09尚无真实教师批准与正式学生端深度发布。故本批重点选择K00/K01扩展25–36页，K07数学条件实例，K08/K09安全回归，而不把工程编辑数当成官方知识总量。

## K00/K01｜78条新来源线索，12个印刷页

新增源文件：
- curriculum/highschool_math/k00_batch57_source_spans.tsv：**78条原创数学及教学要求释义**，每条定位印刷页、PDFKit行范围、来源类别、选学标记、先决条件、课程轨道。
- curriculum/highschool_math/k00_batch57_pdfkit_span_attestations.json：78个不可伪造为正式教研认证的SHA256行区间指纹；与61页既有页指纹及完整原PDF SHA校验。图像不提取为文本。
- scripts/build_kb_batch57_source_review.py：可重放生成/校验来源审查JSON及Markdown，并进行课程轨道、来源SHA、选学标志、重复位置、跨页未认证、教师批准伪造等拒绝。
- docs/evaluation/KB_BATCH57_SOURCE_SPAN_REVIEW.json/.md：源页审查台账与条目条件、未完成门禁。

78条分类：50个CONTENT源定位，13个教学提示，6个学业要求，3个数学建模/探究活动要求，3个标星选学**源位置记录**（涉及2个主题，不能当作3个不同必授主题），2个待看图证据位置，1个选择性必修轨道边界。

覆盖的来源：印刷第25–30页平面向量/复数/立体几何，第31–33页概率统计，第34–35页数学建模与探究，第36页评价与选择性必修范围分界。第35页PDFKit中建模流程图为控制字符乱码；**不把乱码推断为可认证的图示知识**。第27页复数三角形式及第29页几何史选学不计为考试必授。

当前61个原课标内容来源页：**22页存在局部定位、39页仍未经过本系列来源定位、0页完成全页真人教研原子化审查**。与Batch56合计130条非去重来源位置，不等于130个知识原子，更不等于已完成课程讲义。七轨官方知识原子分母全部为null，313仍仅是项目自编编辑候选，不能由301篇待审稿和12条历史关联宣称官方完整覆盖。

## K07｜9类独立有界精确数学检查

新增 backend/app/kb_batch57_exact_witnesses.py 与原创数学条件审核说明 KB_BATCH57_MATH_VALIDATION_NOTES.md。九个算子：
1. 非共线三点唯一确定平面的有限向量叉积见证；
2. 线与平面“交一点/包含/平行不交”的分类，区分平行方向与真正不相交；
3. 非零向量的数量积与垂直，拒绝零向量角度；
4. 严格三角不等式下余弦定理精确实例，不冒充SSA唯一解；
5. 有理复数除法和非零除数、乘回验算；
6. 有限样本空间**显式等可能前提**下的古典概率；
7. 2×2有界联合概率表的独立性/互斥区别；
8. 按总体层规模的分层均值加权，**不认证抽样设计与无偏性**；
9. 样本方差分母 n 与 n−1 的严格区别，禁止 n=1 时假装修正方差已定义。

所有算子仅接受受控整数/Fraction或有限序列与严格字段；浮点、伪认证、任意学生自由文本和非法数学前提均拒绝。返回 FINITE_EXACT_CASE_ONLY / NOT_FORMAL_GENERAL_PROOF / teacher_approved=false / student_solution_verified=false，不能取代数学证明。

## K08/K09｜RAG与Tutor实际调用

新增 backend/tests/test_kb_batch57_source_review.py，包含针对**全部78条来源的逐条状态/来源指纹回归**、12页数量约束、伪选修、虚假教师批准、图像语义伪造、跨轨道、原件SHA漂移及9类算子的正反例。选取13个跨几何、统计、建模及选修边界的未批准source ID，实际调用 student_evidence_lookup 和 draft_next_question，得到 NO_APPROVED_EVIDENCE/ BLOCKED，教师完整解答不返回，未调用任何云端模型API。这是离线真实代码路径的隔离回归，**不代表生产模型质量验收**。

CI和Mac全量脚本新增Batch57生成器 --check。CI只检查已承诺源码快照的一致性，不声称在GitHub Runner上重新打开原PDF。

## 实际Mac完整测试（原始日志已提交）

| 检查 | 实际结果 / 原始日志 |
|---|---|
| 新增专项 | **163 passed / 0 failed**，incremental.log，exit=0 |
| 本地原件PDFKit来源校验 | 原PDF + 全部61页页SHA + 新78条片段SHA核对成功 |
| Python全量 | **43,436 passed / 0 failed / 1 third-party warning**（已包含163新增测试），mac_check_full.log |
| Node | **111/111 passed**，同上 |
| Tutor策略 | **33/33 passed**，同上 |
| RAG困难负例 | **40/40 passed**，Top3 **22/22**，同上 |
| mac_check.sh | **EXIT=0**，mac_check.exit |
| Chrome/Playwright | **15个脚本通过**，mac_browser_full.log |
| browser pytest | **2 passed / 0 failed**，同上 |
| mac_browser_check.sh | **EXIT=0**，mac_browser.exit |

全部日志路径：evaluations/results/2026-11-09-kb-batch57/。浏览器数据库为临时**合成数据**，iPad缩放/压感为浏览器指针模拟，不能冒充真实iPad硬件认证。没有外发任何真实学生资料。

**真实开发中的环境问题**：新独立worktree不带.venv，第一次专项调用报缺少本地Python可执行文件（不是测试断言失败）；按已有Mac模式在本worktree建立指向上一批验证虚拟环境的忽略symlink，随后163项专项通过。完整Python、Node、RAG、浏览器均成功。mac_check会重写两个历史评测JSON（包含当前worktree路径），验收后仅在**Batch57独立worktree**中将这两个无关输出恢复到基线，未碰Mac主仓或其他项目。

## 残余风险与下一整批

- 继续第37–73页的选择性必修/选修课标定位、视觉原件证据，补审第13–14页及第35页建模图；之前定位的22页也必须完整逐条教研原子拆分、跨页数学等价/可选性核验。
- 在经核实的正式课程原子目录下发现真实缺失的内容后，再成模块建设定义、完整假设及证明、反例、两道以上例题、题族、提示与迁移；避免重复堆叠项目编辑主题标题。
- 历史538条未形式认证步骤、10组冲突均需真正数学核验与教师裁决。教师正式批准0，学生端深度发布0；真实模型API冻结对照评测尚未完成。
- 所有课程材料保持 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED；Draft PR不请求合并。GitHub远端提交与CI核验后在Issues #17/#18/#19/#21/#22/#23/#25/#26/#27记录回执。
