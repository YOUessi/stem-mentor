# STEM Mentor｜Batch40 原始课标条款范围复核与七类有限数学核查

日期：2026-11-08。唯一生产/测试环境：授权 MacBook Air；独立 worktree `~/Documents/文件/stem-mentor-kb-batch40`，分支 `feat/kb-batch40-official-clause-evidence`。未使用 Tang / GPU / 模型 API / 真实学生数据；主仓 11 项历史未提交变更未触碰；没有合并或重写 main。

## 基线和 GitHub 依赖

- 上游 Batch39：GitHub Draft PR #64，远端 `e58297db640795f88398130dcf885e278e7329db`；Mac Batch39 本地 `80272b9f65d2660695309f93e827063e4bdf5e57`。两者 Git Tree 均为 `38cc8d90af163e8f98fb88f5407a6af1f6a376dd`，已使用真实 `git fetch` 核实。
- 相关开放任务：#17 主任务、#18 K00、#19 K01、#23 K05、#25 K07、#27 K09；其他 #20–#22、#24、#26 均维持 OPEN。
- 之前 Batch36 47 条历史关联：12 `CLAUSE_UNVERIFIED`、27 `PARTIAL_SCOPE`、8 `CLAIM_MISMATCH`。Batch37–39 已分别为后两类编制新的教师侧审核稿，本批不将这些新的审核稿升级为 APPROVED。
- 本批首次源代码提交：`7077f0a8db2b26f91a45bb5fb3a300ef09b1d8fb`；原始源码 Git Tree `95b63b9429c82f18485ec5b463dbc6ef1b85232b`。追加运行日志/报告和 GitHub 祖先历史衔接后可能产生后续提交；最终 HEAD 以 Draft PR #65 和远端实际 Git ref 为准。

## K00｜从原始课标 PDF 直接核对 12 项选修课程编辑候选

以教育部《普通高中数学课程标准（2017年版2020年修订）》为原始资料。Mac 本地 PDF SHA256 冻结为 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`，使用 Swift PDFKit 在 **9 个实际印刷页**定位短语并建立页面文字 SHA256 指纹；PDF 188 页，印刷页对 PDF 0 基索引偏移为 +7。未提交原 PDF 或课标长段落，也没有把脚本核对视作教师批准。

逐个对照 `k00_batch36_47_legacy_scope_reviews.tsv` 对应的 12 个旧 `CLAUSE_UNVERIFIED` 编辑候选，结果为 **6 个与来源主题显式对应 (`DIRECT_SCOPE`)、1 个仅部分推导 (`PARTIAL_DERIVATION`)、3 个主题存在但未显式单列该目标 (`TOPIC_ONLY_NOT_EXPLICIT`)、1 个应用情境 (`CONTEXTUAL_APPLICATION`)、1 个学校自选选修 (`LOCAL_ELECTIVE_OPTION`)**。逐项原始页码、短锚点、数学范围限制、旧稿 ID 与旧稿 SHA256 在 `curriculum/highschool_math/k00_batch40_twelve_clause_adjudications.json` 和 `docs/evaluation/KB_BATCH40_TWELVE_OFFICIAL_CLAUSE_AUDIT.json`；易读结论在 `KB_BATCH40_CLAUSE_SCOPE_NOTES.md`。

关键负面结论：统计假设检验并不意味着“p 值”为课标逐字明确的独立知识原子；数学微分的线性近似余项、变上限积分求导同样不能未经核对就算独立必授条目；E 类学校自主选修示例不能计入国家统一必修。**12 项原有关系均未获得官方原子等价认证，更未认定旧稿覆盖了数学教学目标**。

## K01/K07｜封闭有限数学见证与严谨拒绝

新增 `backend/app/kb_batch40_exact_scope.py` 的七类受控 `fractions.Fraction` / 整数验证：

1. `1/n → 0` 的 ε–N 有界构造（ε=1/12，N=13），注明实数数列量词顺序。
2. `x²` 的 `Δy` 与 `dy` 不同（x=2，h=1，差为 1）；此算子要求非零增量是**为了展示不相等情境**，不是宣称 h=0 时微分非法。
3. 零假设下尾事件概率 1/20 与给定两假设先验模型下后验概率 1/91 的区别；单个 P(E|H0) 若不满足检验统计量和极端性条件，不擅自称作 p 值。
4. Cobb–Douglas 正投入示例 A=2、L=3、K=5 得 30；不得将经验模型当成必然现实规律。
5. 两个从 t=0 起始的理想化整数节拍 4、6 最小正共同周期 12；不能用于直接保证真实演奏同步。
6. 仿射差分方程 `x[n+1]=a*x[n]+b` 的 `a=1` 分支（结果 14）与 `a≠1` 分支（结果 15），严格处理除零。
7. `∫₀ˣ t² dt = x³/3` 的有限多项式例（x=3，函数值和导数巧合均为 9），明确这不是一般定理证明。

全部有精确有界整数域、输入字段白名单和布尔/字符串/未知算子拒绝。数学解释、条件、反例及证明边界见 `KB_BATCH40_MATH_BOUNDARY_JUSTIFICATIONS.md`。返回状态限 `FINITE_EXACT_CASE_ONLY` / `CONDITIONS_NOT_ESTABLISHED` / `UNSUPPORTED`；始终 `proof_certified=false`、`teacher_approved=false`、`student_step_verified=false`、`student_publishable=false`。七个课程方向官方知识原子**完整分母仍为 null**，无法据此宣称正式覆盖率。

## K09｜Mac 实际运行与复现

- Batch40 增量专项：`88 passed / 0 failed`（`evaluations/results/2026-11-08-kb-batch40/targeted_final.log`）。含 12 关联来源/页码/旧稿 SHA、12 禁止认证、12 单条伪批准注入、12 课程分类篡改、缺证据/错误 track/页码、七算子合法与前提无效实例、字段注入/超范围/类型负例及冻结数学结果。
- 全量 `scripts/mac_check.sh`：**Python 37,990 passed / 0 failed / 1 条第三方依赖警告；Node 111/111 passed；教学策略 33/33；RAG 困难负例 40/40，Top3 22/22**。原始运行证据：`mac_check.log`。
- Chrome/Playwright：15 个脚本全通过，浏览器 pytest 2 passed（`browser.log`）。临时合成数据库；iPad 压感和手势是浏览器指针模拟而非真实硬件；无学生数据上传。
- 原版 PDFKit 短语存在及 JSON 重建检查 `CHECK=True`（`original_source_pdfkit_verified.log`）。CI 在没有原始 PDF 时只检查生成数据与指纹冻结一致；**不能声称 CI 本身重新阅读过原始 PDF，也不能替代教师审校**。
- 当前源代码检查和测试均无新失败；常见高风险反例纳入自动回归。所有提交内容原创，不上传课标版权原文或学生数据。

## 未完成门槛与下一批

- 本批新增**完整讲义 0 篇**；原先 287 篇结构化深度草案和独立选修教师侧审核稿仍为 `REVIEW_PENDING`，正式教师批准 0，学生端深度内容正式发布 0。
- 12 条旧课程联系得到**来源主题分类**，不是 12 条教师批准的官方等价映射；需要继续人审数学等价、是否拆分新原子，以及与教材/教学层次差异。
- 必修/选择性必修/选修 A–E 共七类官方完整知识原子分母仍为 null；课程页码检查和项目自编候选数量不能替代这一分母。
- 旧 538 条待形式认证证明步骤与 10 项未决数学冲突继续保持 OPEN；有限见证不改变该统计口径。
- 下批优先：按七个 track 原始课标建立唯一 ID 和编号/未编号完整来源清单，教师审查 12 条编辑目标的范围与数学等价性，将真实缺口转换为必修/选择性必修的成批原创概念、定理、题族；将范围拒绝与防剧透纳入教学 Agent 的索引/契约测试。不得在缺少人审时提升发布状态。
