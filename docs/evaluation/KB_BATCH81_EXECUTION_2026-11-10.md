# STEM Mentor｜Batch81 开发与验收报告（2026-11-10）

> 本批仅在授权 MacBook Air 的独立 worktree `~/Documents/文件/stem-mentor-kb-batch81` 开发，基线为 GitHub 已核实 Batch80 源码提交 `2e1dc8062c27f1c681ea2acb9be542e29741255c`；主仓11项原有未提交修改保持原状，没有使用 Tang。以下所有教学资料未经真实教师审查，不是正式课程知识发布。

## 优先级及本轮修复

**K07 风险统计口径缺陷**：Batch80 及前序报告中的“P0 127条 / 未有草案91条”实际只计算了 `P0_GUARD_AND_COUNTEREXAMPLE` 这一个子类。完整冻结历史账本中的高优风险前缀 `P0_*` 共 **182条**，还包括：
- `P0_HUMAN_ATTENTION`：14条；
- `P0_REVIEW_IF_DOMAIN_OR_EQUIVALENCE_MISSING`：22条；
- `P0_UNVERIFIED_STEP_REQUIRES_DOMAIN_CHECK`：19条。

这另外55条此前没有被“127条P0 guard子类”的仪表盘口径覆盖，属于**统计范围误解而非新增的历史证明步骤**。本批新增完整P0审查清单，保留全部538条历史证明账本分母、来源SHA及10组未裁决冲突。Batch80原有待审卡36项，本批新建12项，合计48项教师草案；**真正全P0无草案余量由146降至134**（guard子类由91降至79）。

**K00 范围透明性**：将428个官方课标来源锚点按原始轨道及结构角色分配审核通道，保留页码、PDFKit行号、来源哈希及父来源区间；27个SECTION_LABEL、84个MAJOR_NUMBER、185个SUBCLAUSE_NUMBER、132个CIRCLED_ITEM仅是行结构类别，**不是官方原子分类**。七轨分别为必修142、选择性必修101、选修A69、B70、C29、D17、E0。E的0条锚点不代表选修E有0个课程原子，而是学校选用模块需独立分母。61页实质性教师原子化仍0/61，七轨正式原子分母仍全部未知。

## K00 42个真实来源锚点的原创语义分诊（仍非教师认证）

本批从428项机器审计锚点中，对**42项（六轨各7项）**制作带真实源页码/行号/源行哈希、父分区和原始课程轨道的逐条**项目级原创改写**，不复制课标PDF原文；相应文件 `curriculum/highschool_math/kb_batch81_semantic_authoring.json`、生成器 `scripts/build_kb_batch81_semantic_triage.py`、产物 `docs/evaluation/KB_BATCH81_SEMANTIC_TRIAGE.{json,md}`。角色分布：11标题、13混合课程要求、6数学要求、2能力要求、10应用场景。另有386个锚点未进行这样的人工语义草案分诊；选修E仍须按学校实际课程另建目录。本批不将可分拆的数学候选、同名课程条目或章节标题直接计为官方知识原子，任何跨轨数学等价关系均保持待独立审核。

原创分诊第一次生成发现错误门禁：它要求所有非标题均至少提出一项数学原子，导致合法的**建模应用小节标题**被误判。已修复为仅数学要求和混合条款必须提出临时拆分候选，纯能力要求或应用场景允许0项；标题不得伪造数学原子。额外新增`backend/tests/test_kb_batch81_semantic_triage.py`逐条测试42项真实来源坐标、冻结的428条来源清单SHA `f9c2f95a7cd6a49383769b88762eee79f6366ff744a19d865f6be3674e28653e`、课程轨道、防批准伪造、候选遗漏和三项跨轨关系。Mac在本地缓存的合法课标PDF及全部所选PDFKit文本页均重验SHA，`--verify-local-source`成功；CI使用已冻结入库来源的`--check`，不依赖Mac私人缓存。

**K00真实性边界**：42/428只表示拥有待教师审核的独立编辑提案，428本身也是来源锚点而非官方数学知识分母；官方完整原子分母仍未知，逐页完整教师复核依旧0/61。

## K02–K07 数学内容与有限核验

新增12篇原创待审教师论证卡、24道有教师端解答的典型/条件反例题、36段三步推导、12组前提失效案例、36条提示及24项近远迁移。选题：三维两点距离、严格线面平行、两圆交点数、抛物线焦点与准线、椭圆切线、实对数商法则、实二次方程判别式、向量正交平方范数、概率并集上界、离散协方差、椭圆焦距和圆一般式配方。涉及 K02 函数、K03 空间/解析几何、K04 概率统计及 K06 题族。

`backend/app/kb_batch81_math.py` 对每类执行一次正向受限整数/精确有理数计算及一次失效前提拒绝。所有校验结果分别标记 `FINITE_EXACT_WITNESS_ONLY` 或 `CONDITIONS_NOT_ESTABLISHED`，绝不作为一般定理形式证明。定义域、向量维度、零法向量、直线位于平面内部、圆切退化、切点不在椭圆、负对数真数、a=0、非正半径、非法概率质量、零分母、不精确浮点及布尔值均属于负面测试对象。

**安全发布约束**：12份新增卡及之前36份均为 `REVIEW_PENDING/TEACHER_ONLY/NOT_FORMALLY_VERIFIED`；所有正式教师审核0、学生正式深度发布0。对带有实际批准知识文档的测试索引，测试12份教师解答不可经学生检索泄漏。

## 版本化源码与检验路径

- 历史风险与锚点分轨：`scripts/build_kb_batch81_risk_census.py`，固定 Batch80 源输入 SHA，生成 `docs/evaluation/KB_BATCH81_RISK_CENSUS.{json,md}` 与 `curriculum/highschool_math/kb_batch81_anchor_triage.json`。
- 原创内容、完整来源步骤及教师可见性校验：`knowledge/editorial_review/kb_batch81_authoring.json`、`scripts/build_kb_batch81_twelve_cards.py`、`knowledge/editorial_review/kb_batch81_twelve_math_cards.json`。
- 数学验证：`backend/app/kb_batch81_math.py`；负面回归与 K08 学生检索安全：`backend/tests/test_kb_batch81_census_cards.py`。
- Mac 与 GitHub CI 均加入新生成物 `--check`，对源材料漂移、审核状态伪造、数学前提失效及教师答案泄漏采取 fail-closed。

开发阶段首次运行新专项：**817 passed、3 failed**；失败原因是三项历史冲突先走`INDEPENDENT_CONFLICT_ADJUDICATION`通道，测试错误地一律要求`TEACHER_REVIEW_OF_EXISTING_DRAFT`。修复测试断言后重跑 **820 passed、0 failed**。失败是本批新测试的优先级设计问题，不是三项数学证明已被裁决；完整失败与成功结果均保留验收记录。

## 正式验收状态

- 最终 Mac 合并专项 `semantic_and_math_specialty.log`：**1,164 passed、0 failed、退出码0**，其中旧 Batch81 风险与数学专项820项，新增K00来源语义负面/回归344项；这1,164项包含在全量内，不能累加。
- 最终 Mac 完整回归 `mac_full_after_semantic.log`：**55,879 passed、5 skipped、0 failed、1条第三方依赖警告**，Mac `mac_full_after_semantic.exit=0`。其中前一版只含K07的历史基线为55,535 passed、5 skipped；本批增加的344项K00测试已在最终全量中体现。Node **111/111通过**；Tutor策略及RAG离线回归也在完整日志中执行，未调用模型API。
- Mac浏览器回归 `mac_browser.log`、`mac_browser.exit=0`：**15个 Chrome/Playwright 脚本通过**，浏览器pytest **2 passed**；包括课程页面、极值边界、笔/触控/iPad模拟及不同响应式宽度；无页面错误、外部请求或学生真实数据写入。iPad输入为浏览器模拟，**不是物理iPad验收**。
- GitHub最终源码 SHA / Tree、CI运行ID及 Draft PR：交付成功后补写并以远端GitHub为唯一事实源。

## 后续批次重点

1. K00：在 Mac 上对照合法来源课标PDF原文逐条完成数学语义分类/跨页去重，建立必修、选择性必修、选修A–E真正的课程知识原子分母；不得仅用428行源锚点代替。
2. K07：继续审查剩余134项P0（guard子类79；其他P0子类55），并由独立数学教师裁决10组历史冲突及严格证明有效性。
3. K02–K06：继续由源证据驱动扩展正式定义、定理前提及完整原创讲义，补齐题族、反例、迁移和条件验证。
4. K08/K09：加强学生自主求解时的`UNSUPPORTED`/未验证响应与防教师答案泄漏；全部真实教师批准、版权审核及课程完整性前提满足前不得正式发布。
