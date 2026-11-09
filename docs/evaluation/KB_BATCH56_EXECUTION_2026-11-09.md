# STEM Mentor｜Batch56 Mac 课标来源片段精细审计、数学前提见证及 RAG 门禁

## 源码、工作环境和任务选型

- 日期：2026-11-09。**唯一代码开发、数学内容生产与测试设备为授权 MacBook Air** `YOUTangdeMacBook-Air.local`，独立 worktree `~/Documents/文件/stem-mentor-kb-batch56`，分支 `feat/kb-batch56-source-span-triage`；以 Batch55 Draft PR #80 的真实 SHA `b8883e8072452bb51ba9450ab07d650c044b0686` 为基线。主仓原11项未提交修改保留；不在 Tang 开发、不强推或合并 main。
- 先通过 GitHub connector 读取 #17–#27（11 项仍 open）的 issue 正文、最新评论和最新 PR #79/#80。识别最高阻断为 K00 官方法定知识原子分母未认证、K01 标星选修/学业要求类型可能混计、K07 538 未认证步骤及10冲突；本轮聚焦 K00/K01/K07/K08/K09 可联动的实证任务。
- 原件：教育部《普通高中数学课程标准（2017年版2020年修订）》，Mac 本地 `/private/tmp/stem-mentor-official-math-2020-batch51.pdf`，SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`，188 PDF 页。Mac PDFKit 实际重新读取并核对印刷13–73页共61页文本SHA；本轮重点逐段阅读印刷 **15–24 页**，不提交PDF或受版权保护的长段原文。

## K00/K01：52项课程来源片段的可重放精细定位

- 新建 `curriculum/highschool_math/k00_batch56_compulsory_source_spans.tsv`：**52项原创来源要求编辑释义**，逐条含印刷页、PDFKit 行区间、内容/学业/教学/标星分类、原创建议、数学边界风险。
- 其中 **44项内容要求、5项学业要求、1项教学提示、2项明确标星选学项目**；标星2项为函数发展史和对数概念史。第19页脚注明确标星为选学，不作考试要求。不能把标星项目简单升级为全国统一考试必授定理；不能把学业要求重复计入“新增独立知识原子”。
- `curriculum/highschool_math/k00_batch56_pdfkit_span_attestations.json` 保存52条来源片段的 **PDFKit 文本SHA256**，覆盖全部61页的原有页指纹；不提交课标原文/PDF。每条候选记录原件总SHA、页SHA、片段SHA、印刷页、PDF页索引、同页313编辑候选发现线索、可审核状态。
- `scripts/build_kb_batch56_source_span_review.py` 具有独立 `--check` 可重放门禁和 **Mac真实原件复验** `--check --verify-source-pdf <pinned.pdf> --source-dir /private/tmp`。本轮对61页逐页原件SHA复验均通过，52片段哈希与原件对应。GitHub CI 只复验版本化证据及生成一致性，不能声称CI重新读取版权原件。
- 建立 `docs/evaluation/KB_BATCH56_COMPULSORY_SOURCE_SPAN_REVIEW.{json,md}`，10页被**部分人工定位审计**，还未完成10页的所有要求拆分，更不代表整个61页源课标完成教师原子化。
- **313项项目编辑候选不是官方知识点分母，52项片段也不是新增52篇完整讲义。** 七轨（必修、选择性必修、选修A–E）官方原子分母全部继续 `null`。数学等价、跨页去重、教师批准、学生正式发布均没有自动升格。

## K07：8类确定性数学条件见证与非例

新增 `backend/app/kb_batch56_scope_witnesses.py`，只接受有界整数/精确 Fraction 与严格字段集合，支持：

1. 相对全集的有限集合补集，拒绝全集外元素、重复元素；
2. 有界布尔论域下全称/存在命题否定，拒绝伪布尔值；
3. 非负数 AGM 的精确平方差及等号条件，拒绝负数输入；
4. 真正二次式的判别式实根数，拒绝二次首项系数零；
5. 正底且不为1的指数函数整数幂与单调方向，拒绝底数越域；
6. 有理单位圆三角恒等、正切计算，拒绝余弦为0与伪单位圆；
7. 连续多项式端点异号的有理数单次二分，**只认证至少存在一个零点，不认证唯一性**；
8. 合法底数的对数/指数整数次幂互逆关系受控见证，拒绝非法底数。

全部返回 `FINITE_EXACT_CASE_ONLY / NOT_FORMAL_GENERAL_PROOF`，不认证一般定理、学生自由证明、真实教师审核或课程来源条目认证。数学负例和域检查是独立编写的，而非依赖生成模型自评。

## K08/K09：真正执行的内容隔离和双环境测试

- 新增 `backend/tests/test_kb_batch56_source_span_review.py`，**118项新增测试**，包含逐片段来源 SHA 与状态核对、52项类别/数量、伪课程分母/批准/发布/来源漂移的拒绝、8类数学边界和参数化精确实例。
- 还对11项跨类别未批准课标片段实际调用 `student_evidence_lookup` 和 `draft_next_question`，均不得取得审核教师完整解答、不得调用云端模型。
- 首次创建 TSV 时发现部分记录缺少必填的标星字段（52行中51行是6列），严格 Schema 拒绝；已全部补齐。随后本地 PDFKit 全61页摘要核对发现 **第35页包含回车符**，测试最初使用 Python text 模式标准化换行导致页面 SHA 错误；已改为对原始UTF-8字节直接哈希，随后原件验证通过。另修复3项原创释义过短并补足严谨条件；这些属于开发中被真实门禁发现的失败，已解决。
- Mac专项：**118 passed，0 failed**（见 `incremental_initial.log`；首次正式专项运行即成功，前述问题发生在生成器自检阶段）。
- Mac Python全部：**43,273 passed，0 failed，1条第三方依赖 warning**（包含118专项，不重复相加），详见 `mac_check_full.log`。
- Node **111/111 passed**；Tutor政策 **33/33 passed**；RAG困难负例 **40/40** 和 Top3 **22/22**；`scripts/mac_check.sh` **EXIT 0**。
- Chrome/Playwright **15个脚本通过**；浏览器 pytest **2 passed、0 failed**；`scripts/mac_browser_check.sh` **EXIT 0**。原始日志见 `evaluations/results/2026-11-09-kb-batch56/mac_browser_full.log` 与 `mac_browser.exit`。浏览器使用合成数据，iPad触控/压感为CDP指针模拟，不是真实硬件验收。
- 当前静态证据目录：`evaluations/results/2026-11-09-kb-batch56/`。Mac 检查额外写出的两个历史报告JSON为独立worktree产生的无关路径漂移，已在Batch56工作树恢复为原Git基线，没有修改主仓。

## 未完成条件与下一批

1. K00必须继续从原课标逐页完整拆分编号与未编号要求、学业要求、教学提示、标星选修、图示；下一批优先印刷25–36页（几何代数、概率统计及建模活动），随后37–73页；跨页同义项由独立教师逐项判断。直到完成61页全面审查和教师核验前，七轨正式分母一律为 `null`。
2. K01/K02–K06对真正新发现的缺漏继续成批写原创定义、定理/证明、前提、反例、题族、三级提示及近远迁移；当前这52条是来源定位而非可直接使用的52篇讲义。
3. K07现有 **538条历史未形式认证证明步骤、10组未裁决冲突**原样阻断，有限算例不替代形式证明和教师数学复核。
4. K08/K09尚待合法教师签字、审核发布凭据、已批准索引及冻结的真实LLM API/规则基线对照评测。真实教师批准0，学生端深度发布0。所有 PR 均保持 Draft，不自动合并 main。

**Batch56源码提交 SHA `023890ea93baf13d1804765a3b5bf9299e3c1a4c`；最终报告及测试日志单独提交（以最终GitHub HEAD为准）。远端Draft PR及GitHub Actions最后回执以本轮GitHub实际核验为准；不得提前声称CI成功。**
