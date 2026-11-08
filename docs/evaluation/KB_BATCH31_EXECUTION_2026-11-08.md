# STEM Mentor｜Batch31 K00 × K01 × K07 × K09 实际开发与验收

**日期：** 2026-11-08。**唯一开发和测试机器：** `YOUTangdeMacBook-Air.local`。**独立工作树：** `~/Documents/文件/stem-mentor-kb-batch31`；分支 `feat/kb-batch31-source-atom-and-qa`。GitHub 基线：Batch30 Draft PR #55 的远端 HEAD `d1fcf923c730a7505a70e27e166a8a7a693ffc6b`，文件树 `17b391a566c1389b839b85b537b84da52b05cf93`。主仓 `main` 带有历史未提交改动，未触碰、未合并；未在 Tang 开发，没有学生真实数据、API 密钥或版权教材全文进入本仓库。

## 1. 本批 K00 官方来源与原创学习目标候选

从教育部《普通高中数学课程标准（2017 年版 2020 年修订）》原版 188 页 PDF 下载到 Mac 的 `/tmp`，独立核对原文件 SHA256 为 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。本轮利用 macOS PDFKit 读取印刷页 15–28 的 14 页内容；独立渲染并检查印刷页 15、16、19、20、25、26、27、28 共 8 页原始版面，版本化留存每页图像 SHA256（无版权原图入库）。与前批已检查的印刷页 52 合计有 9/61 页经 AI 图像检查；尚有 46 页未做**内容**检查，另有 6 页只完成 PDFKit 文本初查；教师原版逐页核对仍为 0。所有正式官方课程原子分母及覆盖率继续保持 null。

本批依据原版内容编写了 **87 项项目原创的单技能学习目标候选**，横跨必修课程预备知识、函数、几何与代数中的 12 个承载知识的印刷页面。例：量词双向否定、函数定义域与对应关系、二分法保持区间异号不变量、三角商的非零分母条件、平面向量正交基唯一性、空间三点不共线确定平面。明确标注原版星号选学标记，不把必修主题中的选学材料冒充选修 A–E，更不把历史 317 个编号出现位置等同于 317 个知识原子。**87 是局部原始候选数量，不是官方完整知识原子总数，也不是新增讲义数量。**

源：`curriculum/highschool_math/k00_batch31_core_atomic_drafts.tsv`；构建器：`scripts/build_kb_batch31_atomic_core.py`；审计 JSON：`docs/evaluation/KB_BATCH31_K00_PARTIAL_ATOM_AUDIT.json`。负面检查包含来源 SHA 伪造、错误课程页、类型违规、重复候选、非法星号、伪造审核及图像证据漂移。仓库 `--check` 门禁不需要下载 PDF；Mac 上初次验收时额外使用原始 PDF 和 8 张渲染图验证字节 SHA。

## 2. K01 教师侧先修依赖扩展，不入学生端

现有 287 篇 REVIEW_PENDING 草案中有 133 篇没有权威先修图边（部分可合理为根概念，不能仅凭缺边认定错误）。在 Batch26 的 31 项建议基础上新增 **32 项原创的具体数学依赖编辑建议**，例如：SSA 问题依赖单位圆正弦概念、等比前 n 项和依赖递推定义及 q=1 分支、空间直线斜率的退化讨论依赖直线方程。扩展后的联合编辑候选图共 **63 项**，全图 ID 核实且无环；还有 70 篇无明确图边且无本轮编辑建议。权威课程先修图、教学 Agent 检索结果完全未变。

源：`knowledge/deep/prerequisite_editorial_candidates_batch31.tsv`；构建：`scripts/build_kb_batch31_graph.py`；审计：`docs/evaluation/KB_BATCH31_PREREQUISITE_EDITORIAL_REVIEW.json`。伪教师签名、孤儿 ID、双向循环、重复边、短理由被测试拒绝。

## 3. K07 数学实例条件与证明边界

新增 **12 类有界、类型严格的精确有理数算子**，逐项对应合法实例与非法条件拒绝，且分别有数学依据说明。范围包括有限补集、乘负数翻转严格不等号、二次判别式、AM–GM 平方差、整数幂的精确对数、单位圆正切、有限等比和、仿射二分、非零向量垂直、三点唯一确定平面、复数除法、有限量词否定。其中**等比有限和是跨主题附加验证器，没有冒充本批课程页面的来源对应**。

验证器位于 `backend/app/kb_batch31_core_exact_instances.py`、配套输入位于 `knowledge/proof/batch31_core_instance_fixtures.json`，分步论证及反例见 `docs/evaluation/KB_BATCH31_MATH_WITNESS_JUSTIFICATIONS.md`。精确运算成功状态仅为 `VERIFIED_FINITE_INSTANCE`；失效为 `CONDITIONS_NOT_ESTABLISHED`。**全部算子固定返回 `complete_theorem_certified=false`、`student_step_verified=false`、`teacher_approved=false`、`official_curriculum_atom_verified=false`。** 538 条既有自然语言证明步骤仍未形式认证；127 条 P0 有编辑条件稿但尚未被独立形式核验，10 项历史内容冲突未裁决。

## 4. 真实 Mac 回归与失败修复

- 新增专项 `backend/tests/test_kb_batch31_source_graph_math.py`：最终 **1,596 passed，0 failed**，包含 87 条来源候选检查、32 条依赖编辑检查、数学有限穷举与负面防伪用例。
- Python 后端完整回归：**33,551 passed、0 failed、1 条第三方弃用警告**，详细日志见 `evaluations/results/2026-11-08-kb-batch31/mac-check.log`；Mac 完整脚本退出码 0。
- Node：**111/111 passed**；既有教学策略评测与困难负例检索脚本由同一 Mac 检查运行且通过。不能把它们当作真实学习增益。
- Chrome/Playwright 浏览器回归：在实际 Mac 上用临时**合成**数据库运行，**15 个浏览器脚本通过，浏览器 pytest 2 passed（10.99s），整套退出码 BROWSER_EXIT=0**；完整日志为同目录 `browser.log`。iPad 只模拟触控/压感输入，不声称真实 iPad 硬件测试；没有外部请求或学习者真实数据写入。

失败修复记录：（a）第一次在仓库根目录直接执行 pytest，因未设 `PYTHONPATH=.` 导致 `ModuleNotFoundError: app`，改为标准 `cd backend && PYTHONPATH=.` 运行；（b）最初的编辑候选长度门禁将短但准确的专有名词与数学目标误拒，按项目原创目标最小长度重新核验；（c）修改一个 p19 原创学习目标表达后，`--check` 检出生成的审计 JSON 漂移，显式重新运行固定源构建器而没有自动接受旧成果，随后全部回归通过。最终 `--check` 在 Mac 和 GitHub CI 中均新增执行。初始异常与最终日志均留有记录；对外只以最终实际测试结果为验收数。

## 5. GitHub 事实源与下一批

已测试并首次提交的核心代码 Git commit 为 `a2cd1d56a641f57d28a17ca7259cbbfca6fee46c`，Git Tree 为 `038584a6d0e5eb9381ba6f9046fc0e9e1357af05`，GitHub 新建 **Draft PR #56**（https://github.com/YOUessi/stem-mentor/pull/56），基于 Batch30 PR #55，未合并 main。此代码提交已由 GitHub Actions **#42450350533 Success**（https://github.com/YOUessi/stem-mentor/actions/runs/42450350533）独立核查。随后追加本报告与 Mac 成功/首次失败日志的最终提交，必须再次独立核验远端 HEAD 和 CI；报告不把源码 CI 成功自动等价于最终 HEAD CI 成功。

**本轮新增正式深度讲义：0；新增官方已教师审定知识原子：0；教师审核通过：0；学生端内容发布：0。** 教学 Agent 的正式安全知识接口未修改；课程候选全部处于内部编辑待审核，非权威。

下一批重点：（1）原始课标剩余 46 页未做内容检查和 6 页只文本检查，继续逐页源文核对及未编号要求原子化，覆盖必修、选择性必修、选修 A–E；（2）为 87 个候选建立独立页内段落锚点与完整原创深度讲义映射，结合数学域边界编写整章节内容，而非简单累加文本或标题；（3）逐步形式核验全部 538 条证明步骤，裁决 10 项内容冲突，接受真实教师签署后才可能发布；（4）只把明确审核通过的定理、方法和题族接入教学 Agent，继续防剧透、拒答与未见题评测。全量知识库 DoD 未达成，总任务及 #18–#27 不应关闭。
