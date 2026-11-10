# STEM Mentor｜Batch86 原创课标语义解释、历史P0去重与数学前提审校（2026-11-11）

## 开发约束与上游基线

- 全部内容创建、代码修改、符号核验、Python/Node/浏览器测试在授权 **MacBook Air** 独立工作树 `~/Documents/文件/stem-mentor-kb-batch86` 完成，工作分支 `feat/kb-batch86-source-p0-reliability`；从Batch85的Mac源SHA `651c9a91cde865c80798d4ae0fcfff5f6c55ecd5` 派生。保护主仓11项既存未提交修改；不使用 Tang，不重写 main，不自动合并。
- 先核对 GitHub 总任务 #17、子任务 #18–#27（全部Open），最近上游 PR #110（Batch85，Open/Draft）；其远端HEAD最终为 `24a0eb42a19bde5c05e82c229dca2a5606890023`。**上游 Mac 源提交与远端补充报告提交的 SHA 不相同，Git Tree 应单独核验。**
- 课标基线《普通高中数学课程标准（2017年版2020年修订）》；原始PDF本地SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。PDF和其版权文字仅留Mac；GitHub存独立原创释义、页行定位及来源SHA。
- 所有草案始终 `REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_VERIFIED`，未获取真实教师核验、数学通用形式认证，亦不进入正式学生知识索引。有限算例、源 SHA、字符串完整度绝不等同于上述三类审查。

## K00/K01：89个新的来源锚点及后续完整分母缺口

- 新增 **89个**课标锚点的原创独立数学语义分析和适用条件/失效警告：必修32、选择性必修25、选修A16、选修B16。细分为数学要求48、章节/课程标题28、应用语境9、能力要求4（标题不伪装数学知识原子）。每条保留原PDFKit来源行SHA、页SHA、来源轨道、角色、版本及独立审核状态；可供后续教师拆分的项目级**48个临时主题**尚未跨页去重。
- 项目级来源编辑总进度由249/428→**338/428**，还缺**90**（必修43、选择性必修19、选修A11、选修B17）。选修C/D已有来源释义，选修E目前无可归类来源锚点；这些事实**不等于**官方完整知识原子化、课程可教学覆盖率或教师审核。七轨官方知识原子总分母仍全部`null`；全页教师正式原子化0/61。
- 原创作者集 `curriculum/highschool_math/kb_batch86_semantic_authoring.json`；确定性校验器 `scripts/build_kb_batch86_semantic_review.py`；再生矩阵 `docs/evaluation/KB_BATCH86_SEMANTIC_COVERAGE.{json,md}`。机器门禁拒绝冒充批准/已发布、非法轨道、来源SHA不一致、重复锚点、空数学要求、章节标题混为知识点、与既有来源重复及全量分母伪造。
- 真正课程分母工作仍欠跨页等价/异义核对、必修及选择性必修逐章的完整教师课程分析、选修A–E教育目标对照及授权教师签核；不以428作为官方知识分母。

## K06/K07：10份源SHA绑定P0审稿草案与独立去重纠偏

- 新增**10份**原创、历史原证明步骤ID+原文SHA双绑定的高风险数学教师审稿卡，覆盖对数乘积、二次方程判别式、AM–GM、两圆交点、抛物线焦准线、Cauchy–Schwarz、两事件容斥、向量数量积/夹角、奇数平方和归纳、费马驻点必要条件。每稿含严格条件与命题、3段可审论证、2道教师侧已解原创例题、前提失效反例、合法边界、错因、三级提示、近远迁移；共20道例题、30段论证、30条分级提示、20项迁移。
- **纠正历史重复计数：** Batch85此前声称P0已关联`60/182`，但和Batch81两条重复，实际上当时只有**58个不同历史P0步骤**；本批10张卡仅6个首次覆盖，另外4个为旧步骤的补充审查。因此累计**70个审稿卡链接、64/182个不同P0步骤**，尚有**118个不同P0步骤无审稿卡**。538条历史自然语言证明步骤仍未获得普遍命题形式认证，10组冲突未裁决。测试中对这一去重事实作冻结回归，禁止重复计为覆盖。
- 来源直接绑定、条件验证器只检查其确实支持的**有限精确实例**（复用旧有Batch28 Fraction oracle，新增SymPy独立具体算例）；`student_free_text_verified=False`、`human_teacher_reviewer=null`。新增 `scripts/build_kb_batch86_p0_reviews.py`、`knowledge/editorial_review/kb_batch86_p0_authoring.json`、`.../kb_batch86_p0_teacher_cards.json`、`docs/evaluation/KB_BATCH86_P0_HISTORY_GUARDS.md`，并在CI和Mac检查脚本引入 fail-closed 检查。
- 本轮进一步人工发现并修复三项数学编辑用语：判别式平方根并非“两个非负主值”、`p=0`时焦点**点**落在准线**直线**上而非二者为同一对象、概率零的非空交集应称“零概率样本点”而非“零概率原子”。没有修改冻结历史原件或旧oracle Profile，修复仅施于新的原创衍生审稿材料。加入小范围新回归测试覆盖符号正负号、点与直线、连续型概率零测度交集。

## K08/K09：检索权限、审校状态与独立证据

- 新增 `backend/tests/test_kb_batch86_source_and_p0.py`，逐条覆盖89项来源追踪、10张卡原步骤SHA和来源条件、伪造教师签字、跨轨、重复、内容缺失、非法数学参数、teacher-only解答防泄漏（非空独立合成批准索引）、历史P0来源总量与去重修正。
- Mac原始课标整文件SHA及PDFKit来源逐行SHA校验应与项目程序检查同步执行；GitHub CI只能冻结校验派生源SHA，不能冒充云端复制版权PDF后的逐行核实。
- 真实本地专项、全量Python、Node/策略/RAG、Chrome/Playwright测试以及 CI 的成功、失败次数，以 `evaluations/results/2026-11-11-kb-batch86/` 中最终退出码/原始日志、实际GitHub Actions为准。**不得将运行中的测试或先前测试冒充最终结果。**

## Batch87及更长路线

1. 首先将剩余**90/428**课标来源锚点全部完成项目级来源解释；进一步做跨页跨轨语义去重与教育部原始课程范围溯源，分别形成必修、选择性必修、选修A–E可稽核的**初步正式知识原子候选分母**，对未审核的完整度显式标示`null`，与428来源行区分。
2. 对**118个未关联P0历史证明步骤**按前提遗漏、除零、根号符号、向量退化、导数可导性等分类推进；核查10组历史冲突，教师未审核不自动裁决。
3. 按真正的课程缺口继续建原创完整讲义和题族，包括定义、定理条件、逐步证明、正反例、教师侧完整解答、学生阶梯提示、前置关系和变式；K08仅提供受控证据与不得剧透的学生提示。
4. 继续独立数学检查与实际Mac完整测试，只有教师真实签名且检索权限合规才考虑逐章学生发布；不关闭 #17–#27，不关闭持续续建任务。

## 最终提交、Mac与GitHub远端验收记录

- **Mac终版专项（数学释义修复后）**：`1117 passed in 97.65s (0:01:37)`，退出码 `mac_specialty.exit=0`；增量专项含于全量，不与Python全量重复计数。
- **Mac终版全量（修复后实际重跑）**：`59713 passed, 5 skipped, 1 warning in 491.37s (0:08:11)`，退出码 `mac_full_final.exit=0`；Node 111/111、Tutor策略33/33、困难负例40/40、RAG Top3 22/22，全部在 `mac_full_final.log`。
- **Chrome/Playwright**：15个场景脚本通过，浏览器pytest `2 passed`，`mac_browser.exit=0`，独立Mac真实浏览器执行；未声称真实iPad设备覆盖。
- 保留数学文本完善前的专项及全量快照日志 `mac_specialty_pre_math_editorial_fix.log` 与 `mac_full_pre_math_editorial_fix.log`，区分首次成功与最终版本；只有`mac_full_final.log`才用于终版验收。原始课标PDFKit行SHA已在Mac门禁中核验，云端CI无原PDF。
- Mac版本：Python 3.13.13，Node v22.23.1。最终源码提交SHA及远端CI结果另经Git/GitHub分别验收；无真正教师审核且不发布学生端。

- 原创内容、数学修订和Mac最终测试的源码提交：`37da729d36e8376474c0b7e4a6e2bf240803587d`；对应Git Tree：`ff4c8f908ce210b97716ec020c2f1ffb92c5efb8`。
