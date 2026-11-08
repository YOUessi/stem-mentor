# STEM Mentor｜Batch49 Mac 开发与审核证据（2026-11-09）

## 设备、隔离与 GitHub 事实边界

- 唯一代码/教学内容产出与测试设备：MacBook Air `YOUTangdeMacBook-Air.local`。独立 worktree `~/Documents/文件/stem-mentor-kb-batch49`，分支 `feat/kb-batch49-modeling-inference`；父分支 Batch48 PR #73，基线 `ee5113b085a7df6a661411f6d2b4deb74e575a63`。没有在 Tang 开发，没有合并 main，没有覆盖主仓已有11项未提交修改。
- 依据：仓库内 2017/2020 高中数学课标 PDF 引用锁定 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`，Batch31/32 项目编辑候选原子及页号由 Batch48 overlay 继承。**不是官方全量课程知识原子分母**，每条 `official_clause_verified=false`。
- 源文件：`scripts/author_kb_batch49.py`；原始 20 篇 JSONL：`knowledge/editorial_review/kb_batch49_modeling_inference.jsonl`；内容 PIN 由 `app.kb_batch49_review.SOURCE_SHA` 明示。
- 严格审核状态：`REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED`，无真实教师批准，不允许将学生自由步骤自动认证；没有上传学生数据，未调用外部模型 API。

## 一、20 篇新增原创教师待审单元

**必修 14 篇**：对数概念历史资料证据核查；正弦周期模型的前提与相位；函数模型的定义域/物理约束；线性/指数/对数的渐近比较；模型参数单位与外推；复数极坐标的零模退化；斜二测图示比例与非保角性；空间投影图不构成证明；线面平行的完整前提与反证；位移与路程的向量区分；从样本到总体的抽样机制；建模目标与可核查假设；求解后的残差与现实可行域；结构性模型失效与参数偏差区分。

**选择性必修 6 篇**：微积分发展史料研究方法；按期变化的数列递推建模；导数的物理单位与定义；法向量推理中的线面包含/平行边界；解析几何形成史的来源定位；圆的坐标平移与可逆表达。

每篇保持完整 Schema：正式陈述、适用域与符号/条件、先修、三阶段论证及其依据、明确的错误主张及具体反例、2 道教师侧完整例题与过程、3 级有具体数学针对性的提示，以及近远迁移。合计 **20 讲义、40 例题、20 具体反例、60 分步推理、60 提示、40 迁移练习**。

有关数学史的 3 篇不编造无法独立核对的历史归属或年份，只教有证据来源的研究与引用方法；没有将史料核验方法伪装为一般定理证明。全部 Markdown 与结构化审核记录按相同来源 JSONL 派生：

- `docs/evaluation/KB_BATCH49_MODELLING_MANUSCRIPTS.md`
- `docs/evaluation/KB_BATCH49_MODELLING_AUDIT.json`

## 二、K00 七轨道编辑覆盖矩阵（不等于官方课标覆盖率）

|课标方向|项目编辑候选|直接待审稿|仅旧稿非等价关联|缺直接稿|官方全量原子分母|
|---|---:|---:|---:|---:|---|
|必修|125|125|0|0|null|
|选择性必修|92|72|0|20|null|
|选修A|28|22|6|0|null|
|选修B|29|27|2|0|null|
|选修C|19|17|2|0|null|
|选修D|16|15|1|0|null|
|选修E|4|3|1|0|null|
|**总计**|**313**|**281**|**12**|**20**|**null**|

**关键：全部125项必修“项目编辑候选”已有直接待审稿，仅代表项目内部对应关系，并不意味着普通高中数学必修课标全量内容已完成，更不意味着审核通过。** 原课程标准逐项核实、未编号要求拆分、扩展课程归属、去重及正式知识原子分母仍没有完成；数值 `281/313` 严禁用于发布意义的覆盖率报告。机器矩阵保存每项目标来源页码、原始编辑文件哈希、内容引用及未审状态。完整剩余20个候选见 `KB_BATCH49_PROJECT_SCOPE_GAPS.md`。

## 三、K07 有界数学证据与负例

新增 **17 类有限精确核验**，采用严格字段形状检查、Python整数与 Fraction：

- 正弦四分之一周期预测、线性容量时间边界、有限指数值、速度换算；
- 非零复数的模平方、斜二测缩放长度平方、空间异面直线投影交叉；
- 直线与水平面包含/相交/不相交、平面向量位移平方；
- 有限样本均值、非负线性库存终点、整平方根；
- 三等距样本的线性模型一致性、等差递推指定项、二次位置函数导数；
- 点线与平面关系及坐标平移。

严格拒绝无效的周期、缩放分母、法向量、期数、容量、负库存、越界数值、空样本、额外权限字段、嵌套对象注入、未知操作及自由文本证明。返回状态为 `FINITE_EXACT_CASE_ONLY`、`CONDITIONS_NOT_ESTABLISHED`、`UNSUPPORTED`；不将有限输入结果等同于一般数学定理的严格形式证明，数学史 3 篇没有数值见证。

**审查过程中修复**：正弦幅值 A=0 时不存在唯一的“上穿中心线相位”，已单独说明常值退化；导数与位置关系的反例改用数值与量纲均不同的情况。其余数学论证仍需真人教师核对。

## 四、K01/K08/K09 审核门禁与真实代码路径回归

- 严格 Pydantic 对课程 ID、所属方向、源文件哈希、内容字段、输入格式、内容版本、待审状态进行检查，拒绝伪造审批、版权全文来源以及教师解答公开。
- 课程矩阵按新增稿动态更新，但七轨道的正式 `official_atom_denominator`、`official_verified_coverage` 始终保持 null；真实教师批准0、正式学生发布0。
- 使用已有 `student_evidence_lookup` 和 `draft_next_question` 的真实本地调用，验证20篇未审核讲义不能进入学生提示或完整答案。测试所给 provider 是“不得调用”离线假地址，没有外部 API 调用。
- 增加源数据固定哈希、生成 Markdown/JSON 防漂移、Pydantic 负例、跨课程错配、17种有限检查正反例、313条矩阵审计、历史/数值审核边界、随机小整数枚举及教学 Agent 不剧透回归。Mac `mac_check.sh` 与 GitHub CI 均加入新批 source/check 命令。

## 五、测试原始结果、版本和失败记录

- 增量用例初始版本实测：`391 passed`，见 `evaluations/results/2026-11-09-kb-batch49/incremental.log`。随后进行正弦零幅值与导数反例文案审查并重新生成内容哈希与审核材料；最终数字以最新版复测日志和 `*.exit` 为准。
- Mac 全量：`evaluations/results/2026-11-09-kb-batch49/mac_check_full.log` 和 `mac_check.exit`。
- Chrome/Playwright：`evaluations/results/2026-11-09-kb-batch49/mac_browser_full.log` 和 `mac_browser.exit`；仅合成数据，iPad 模拟不代表实体设备。
- GitHub CI、远端 HEAD、PR 状态与代码 SHA：以最终提交后的远端核验回执为准；**不得用本报告未完成字段推断CI成功**。

## 六、下一批明确依赖与优先顺序

1. K00优先对课标正式原子分母做逐页独立核对、拆分未编号要求；标注教育部标准层级、地方/年份、选修学校自选属性并经过教师审查，先保障全国必修与选择性必修。
2. K02-K06下一批补齐剩余20条**选择性必修项目编辑候选**：概率独立与乘法公式、二项/超几何/正态、相关系数、最小二乘、列联表与研究活动，再检视已完成281条是否真正具备充分的原创教学深度而非仅字段齐全。
3. K07优先审查538条历史未形式认证证明步骤、10项未裁决冲突与12项非等价旧关联；高风险命题逐项审查假设和反例，不能被数值求解器自动“认证”。
4. K08/K09须有真实教师审查、实际可授权发布的版本化索引和冻结题集 API/规则基线对照；当前教师批准与学生端正式深度发布均为0。继续保持 Draft PR，不自动合并 main。

## 七、最终 Mac 实测回执（2026-11-09）

- 修复后基于最终原创来源（SHA256 `a781c7207a8dde638bcbf238ed44e7f2fb21e80bc2b6081f771689a6fc165dc4`）运行 `scripts/author_kb_batch49.py --check`、`PYTHONPATH=backend .venv/bin/python -m app.kb_batch49_review --check`：均通过，内容及审计件无偏移。
- 增量 `backend/tests/test_kb_batch49_modeling_inference.py`：**391 passed，0 failed，exit=0**，`incremental.log` / `incremental.exit`。
- 最终 Mac 全量 `scripts/mac_check.sh`：Python pytest **41,417 passed，0 failed，1条第三方依赖警告**（120.24秒），Node **111 passed / 0 failed**；Tutor策略 **33/33**、RAG困难负例 **40/40**、Top3 **22/22**。`mac_check.exit=0`，日志 `mac_check_full.log`。41,417 已包含新391条增量测试，不应额外累加。
- 真实 Chrome/Playwright 本地浏览器脚本 **15项全部通过**，browser pytest **2 passed / 0 failed**；`mac_browser.exit=0`，日志 `mac_browser_full.log`；使用临时合成数据库，不等于真实iPad硬件认证。
- 原版本审校发现两个内容边界及一个**有限点反例不成立**：零正弦幅值的相位退化、导数单位实例，以及不能用 `x=1/2,b=1.01` 反驳 `x<b^x` 的全称断言。第三处已替换成有效反例 `x=100,b=1.01`（此时 `1.01^100≈2.705<100`），重新生成哈希、Markdown、审计 JSON，随后完整重测（最终结果如上）。这表明语义核查不能由 Schema 字段数量代替。
- 运行旧评测工具自动改写的两份历史合成评测结果 JSON 已在**独立 Batch49 worktree**安全恢复到基线，不把无关变化带入 PR；原始 Mac 主仓11项未提交修改完整保留。
- GitHub 远端 Draft PR、CI 与 SHA 由后续提交回执核验；未得到远端成功响应之前不声称远端 CI 通过。
