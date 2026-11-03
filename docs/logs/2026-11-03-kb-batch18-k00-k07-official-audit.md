# STEM Mentor｜Batch18 K00 官方课标来源核查 + K07 证明/冲突风险审计

日期：2026-11-03。**仅 MacBook Air**，独立 worktree `stem-mentor-kb-batch18-k00-k07`，分支 `feat/kb-batch18-k00-k07-audit`，父提交 `dfece1046fb392ae4b17f1839e0c132c3cd9e34c`（Batch17）；未碰触主仓 11 项原有未提交改动，未使用 Tang。此报告所列成果是**来源核查与有限数学审查**，不是已完成官方课程全量原子审定或自然语言定理形式证明。

## GitHub 验收与依赖

已读取总任务 #17 及 #18–#27 的实际最新状态（全部 OPEN），并检查上游 Draft PR #43（尚未合并），以其提交为新 worktree 基线。不合并主分支，不将源 PDF 或版权教材全文上传仓库。

## K00：权威课程标准与可审计的真实缺口

- 来源：《普通高中数学课程标准（2017年版2020年修订）》，教育部制定。基于教育部门户通知“教材〔2020〕3号”，数学正文以 2017 版课程要求为准、2020 修订数学仅涉及前言。标准 PDF 原件来自昌都市教育局的公开文件：
  `https://jyj.changdu.gov.cn/cdsjyj/c101476/202205/764ee1914e3c45aaba8e372f1b628a34/files/75676dfa9af0442db1457404a884a69f.pdf`。
- 已在 Mac 直接下载源 PDF，另与人民教育出版社下载副本逐字节 SHA256 核对相同，校验和为：
  `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。
- 使用 macOS 原生 PDFKit 提取，源 PDF 188 页；**逐页处理课程正文纸质页码 13–73，共 61 页**。原始源 PDF 和提取的受版权保护原文均仅保留 Mac 临时目录，没有提交 GitHub。
- `scripts/build_kb_batch18_source_register.py` 根据纸质页码、项目课程阶段与段落编号生成不可篡改的来源定位（PDF 页码、短片段的 SHA256、来源 PDF SHA256、编号种类、审核状态）。`docs/evaluation/KB_BATCH18_SOURCE_MARKERS.json` 中共有 **248 个“编号标记候选”**：必修 50、选择性必修 30、选修 A 67、B 62、C 24、D 12、E 3。**248 不是官方原子要求分母**，因为编号中可能包含实例/子项/章节标号，也可能漏掉没有编号的文本。项目提炼的 26 个高层课程主题索引同样**不是**原子知识总数。标准并未提供“官方原子知识 ID”供自动计数。
- 交叉比对既有 `source_anchored_skill_candidates_batch12.json` 的 132 个自编学习目标所标纸质页码（仅页码粗比，不是语义等价校对），找到**三个存在来源编号而该页没有任何既有编辑目标的页**：选择性必修第 40 页、选修 A 第 56/57 页。尤其选修 A 的第 56–57 页为“概率与统计”整块，现有 18 项选修 A 原创候选只覆盖微积分/空间向量与代数部分，未对 A 的统计模块建立任何编辑目标。页 40 涉及数学史中的微积分史课题研究。
- 新增 `scripts/build_kb_batch18_gap_candidates.py` 与 `curriculum/highschool_math/k00_source_gap_candidates_batch18.json`，产生 **10 条人工明确定位的待审补课目标**：选修 A 9 条（连续分布、重要连续分布、数字特征、二维离散联合分布、二维正态、矩估计与极大似然、正态假设检验、拟合优度检验、二元线性回归），选择性必修 1 条（微积分发展史探究）。这是原创学习目标拆解，不是复制课标段落；尚未建立深度讲义、形式证明或教师审核。
- **仍不能声称达到官方原子全量分母**：国家标准课程内容中包含非编号要求，E 类依地方特色和学校自主安排，不适合捏造全国统一细颗粒度必选清单。源标记、编辑目标和教师签核必须由独立老师逐条核对后才可升级。机器审计中 `verified_official_atomic_denominator=null`、`official_atom_coverage_rate=null`、`teacher_approved=0`，既有 132 条不会被新增候选静默改写。
- 可核查输出：`docs/evaluation/KB_BATCH18_SOURCE_MARKERS.json`、`curriculum/highschool_math/k00_source_gap_candidates_batch18.json`，CI 使用 `--check` 拒绝伪造课程完成率与假审批。

## K07：451 条证明义务、10 项冲突与 23 项语义缺口

- 对比冻结 `KB_PROOF_OBLIGATIONS_BATCH07.json`、`KB_CONFLICT_RISK_BATCH07.json`、`semantic_gaps_batch04.json`，使用输入文件 SHA256 冻结来源，严格保留 451 条未完整形式化认证的步骤、10 项未裁决的双版本数学冲突、23 项待关闭的语义深度缺口。
- 在 `scripts/build_kb_batch18_k07_review.py` 中为**全部 10 项冲突**编写独立的受控算术/符号/逻辑边界案例，共 **372 个检查，通过 372**。检查覆盖：复合函数的内外定义域约束、奇偶函数的对称定义域、分段函数交叠、介值定理不保证唯一性及不连续反例、点到直线法向量不能为零、二项分布独立性与边界、超几何分布无放回支撑与归一化、最小二乘的零方差退化、三角形正弦面积公式必须使用夹角、不同维向量无法加法。
- 这些用到 SymPy 的代数事实或 Python `Fraction` 的精确枚举，**不是证明学生自由解答、不是对全部 10 篇文章逐句裁决，更不能将 372 个案例计作 372 个完整定理的证明。** 对相关性与因果关系等不能由有限代数检查覆盖的争议，必须由教师专门判定。
- 形成逐步风险排序审查队列：**P0 22 步、P1 360 步、P2 69 步，合计 451 步**；P0 首先覆盖涉及历史双版本冲突的高风险命题，P1 覆盖可能依赖域、独立性、可逆性、极限、非零条件等论证，P2 留给低风险顺序审核。具体审查顺序为工程启发式，不代表数学正确性评级。
- 保留 10 对 active/candidate 源内容 SHA256，全部裁决仍为 `HOLD_BOTH_SOURCE_VERSIONS` / `OPEN_REQUIRES_INDEPENDENT_TEACHER`，23 个缺口一律 OPEN，没有自动关闭。
- 机器输出 `docs/evaluation/KB_BATCH18_K07_RISK_REVIEW.json`：完整 451 个步骤的证明陈述、草案理由、风险等级与待审状态，372 个独立受控检查和 10 个冲突审查合同。完全不更改知识的 `REVIEW_PENDING`、`TEACHER_ONLY` 和学生端 `NO_APPROVED_EVIDENCE`。

## 测试与真实失败

本批新增 `backend/tests/test_kb_batch18_k00_k07.py`，包含课标页源索引检查、7 路课程标签、编号/链接/审核造假负例、全部冲突案例、K07 证据重构、证明步骤伪通过、10 条补课候选不可发布测试。静态 CI 新增三个审计器 `--check`。

- 初次在 worktree 根目录直接运行 `python -m pytest backend/tests` 导致 21 个收集错误，原因是没有设置既有 CI 要求的 `PYTHONPATH=.`，**不是通过修改旧测试掩盖错误**。改为与 GitHub CI 一致的 `cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q` 后，原有 + 本批套件均成功；初始完整运行 **11589 passed / 1 warning**，后增加 4 个 K00 缺口负例，最终完整复测 **11593 passed / 1 third-party deprecation warning**（`python-full-final.log`）。
- Node 全量 **111 passed**，日志 `node.log`。
- CI 关键流程：`build_kb_coverage.py --summary`、`audit_deep_math_evidence.py --check`、Batch17 源校验、Batch18 来源与风险报告审计均已在 Mac 上通过，日志 `ci-core.log`。
- Chrome 全套历史响应式/实验室回归 **PASS**；iPad 多点触控与压感模拟 **PASS**（`browser.log`，不等于真实 Apple Pencil 硬件测试）。
- 所有原始命令日志存于 `evaluations/results/2026-11-03-kb-batch18/`；新增的 372 个算例和测试为本批真正新增验收，不能用它们代替 451 条完整证明验证。
- `git diff --check` 通过；全部代码在独立 worktree 中生成，Mac 主仓未提交内容原样保留。

## 下一批（依赖顺序）

1. **K00 / #18**：对纸质页 13–73 的 248 个自动编号标记人工去重、认定其是否独立学习要求，补读无编号段落，建立带页码、课程主题、规范文本含义与 teacher-review 的完整逐条**项目可审计原子分母**。选修 A 第 56/57 页的九类统计学要求先补深度讲义，但不因为数量增加而关闭课程缺口。选修 E 依学校地方课程记录适用范围，不能捏造全国统一必学知识原子总数。
2. **K07 / #25**：先处理 22 条 P0 步骤；对 10 对冲突逐条比较“假设→结论→反例→证明步骤”，提供精确来源和可手工复核的裁决证据，**只有真实教师签核才关闭**；继续检查 23 个课程语义深度缺口是否真正被新草案覆盖。
3. **K09 / #27**：保留冻结回归、学生端防泄漏、全文已审签核为零的 fail-closed 状态，单独统计有界算例检查与正式完整证明的差异。

所有权威发布状态保持 `REVIEW_PENDING`，没有进行真实学生数据收集、没有上传源 PDF、没有使用 Tang，也没有自动合并到 main。
