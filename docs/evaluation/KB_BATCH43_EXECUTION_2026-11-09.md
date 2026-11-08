# STEM Mentor｜Batch43 版本化执行报告（2026-11-09）

## 1. 可追踪事实与开发隔离

- 项目：`YOUessi/stem-mentor`；总任务 #17，相关 #18/#19/#20/#21/#22/#24/#25/#26/#27。
- **唯一开发/内容/测试主机**：YOUTangdeMacBook-Air.local；独立工作树 `/Users/youtang/Documents/文件/stem-mentor-kb-batch43`，分支 `feat/kb-batch43-core-depth`。
- 本分支在 Batch42 的最终提交 `490fd41b0dfd11e3ea460ea27caf5ca26f5159f9` 上迭代；原始 24 篇内容源码提交 `e77cea080e206236526130d394f644a2350c7d18`；本轮数学极值漏洞修复提交 `11b0e62f2ea4dcb0af67e5918ca326d0b0384fe5`（Git Tree `4d600376bfe73dbe460b60ceee44bd7886f0cbc9`），该提交 GitHub Actions #42503936180 已核实 `completed/success`。
- Mac 原始 main 工作树 11 项未提交修改未更动；没有在 Tang 开发，没有强制推送、重写历史或合并主分支。
- **Draft PR #68**：https://github.com/YOUessi/stem-mentor/pull/68（基于 Batch42 #67 的独立叠加 PR，不合并 main）；最终 HEAD/Tree/CI 以 GitHub 实际回读为准，不以本地日志推测。
- 内容来源为项目原创编辑稿与此前 SHA 锁定的课标项目条目；课标原始 PDF 的条款逐一对应认证尚未完成，**不能对官方全覆盖作任何结论**。

## 2. 实际批量成果（K00/K01/K02/K03/K04/K06/K07/K08/K09）

### K00 课程范围增量

- 基于 Batch42 冻结的 313 个**项目编辑候选**和课程版本/来源行号/印刷页/源 SHA，新建逐目标覆盖 `KB_BATCH43_PROJECT_SCOPE_OVERLAY.json`；不覆盖旧批审计记录。
- 本批将 **24** 个原本没有直接审核稿的目标转为有原创独立审核稿关联，其中必修 **12**、选择性必修 **12**。覆盖缺稿从 **168→144**，直接待审稿从 **133→157**，仅历史非等价关联维持 **12**。
- 新计数：必修候选 125 / 直连 47 / 未直连 78；选择性必修候选 92 / 直连 26 / 未直连 66；选修 A–E 本批未新增。
- 七个官方课程原子分母依然全部为 `null`；313 不是教育部确认的原子总量，也不能计算有效课标覆盖率。

### K01/K02/K03/K04/K06 内容、审核与例题

- `knowledge/editorial_review/kb_batch43_core_depth.jsonl`：新增 **24 篇**项目原创、具有来源锁和独立 ID 的必修/选择性必修**教师侧待审稿**。领域覆盖集合、命题逻辑、二次不等式、对数、单位圆、数值二分法、向量、解三角形、数学归纳、导数与极值、空间点面距离、解析几何、排列组合、二项式、全概率/贝叶斯、离散期望与方差。
- 每篇包括对象/正式陈述、必要适用条件、前置知识、三段可复核的数学论证、反例或无效应用及错因、**两道教师侧完整例题**、定制三级提示、近远迁移；合计 **48 道教师题、24 项反例、72 层提示、48 项近远迁移**。
- Pydantic 门禁逐项校对 source ID、重复条目、字段完整度、来源、审核及权限；所有稿件保持 `REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED`。**不构造伪造教师批准，不允许学生端检索完整教师解答。**
- `KB_BATCH43_CORE_DEPTH_AUDIT.json` 为每篇记录内容 SHA256、课程来源、验证器、无效前提拒绝、审核界限；`KB_BATCH43_CORE_DEPTH_MANUSCRIPTS.md` 为完整可读待审稿。

### K07 数学有限见证和独立纠错

- `kb_batch43_exact.py` 建立 **24 类**整数、有限集合、有限真假表、`Fraction` 精确运算见证及非法条件拒绝。相关依据与适用域见 `KB_BATCH43_MATH_VALIDATION_NOTES.md`。
- **发现并修复真实反例缺陷**：初始二次函数极值检查器虽然接受 `center`、`shift` 参数，却始终硬编码返回 `MINIMUM|0` 或 `MAXIMUM|0`。对于 `f(x)=a(x-c)²+s`，在 `a≠0` 下应输出极值类型、位置 `c`、函数值 `s`。新增平移 `c=7,s=-5`、凹向下 `c=-4,s=6` 和 `a=0` 拒绝的真实回归测试，更新冻结审计数值。
- 一般定理形式认证 **0**；学生自由文本推导认证 **0**。仅报告 `FINITE_EXACT_CASE_ONLY`，绝不将参数试验误称定理证明。

### K08 学生权限

- 学生检索投影对本批 24 篇待审稿返回 `NO_APPROVED_GOAL_EVIDENCE`，教师完整解答不进入学生文档列表或普通学生提示，编辑元数据需要明确本地编辑范围；本批不宣称真实 API 上线或完整 RAG 对照评测完成。

## 3. Mac 实际测试与失败修复

- 专项最终命令：`PYTHONPATH=backend .venv/bin/python -m pytest -q backend/tests/test_kb_batch43_core_depth.py`，**440 passed / 0 failed**；源码首次提交时的专项运行记录为 439 passed。
- 一次测试命令遗漏 `PYTHONPATH=backend`，造成 `ModuleNotFoundError: No module named 'app'` 的**环境启动错误**，已使用实际项目路径重新执行通过；没有把它当作数学验证器失效。
- 完整命令 `bash scripts/mac_check.sh`：Python 回归 **39,005 passed / 0 failed / 1 条第三方依赖警告**；Node **111/111**；教学策略 **33/33**；RAG 困难负例 **40/40**，Top3 **22/22**；本地 `EXIT=0`。
- 浏览器命令 `bash scripts/mac_browser_check.sh`：**15 项 Chrome/Playwright 浏览器脚本均通过**，浏览器 pytest **2 passed / 0 failed**，`EXIT=0`；使用临时合成 SQLite，原始日志见 `evaluations/results/2026-11-09-kb-batch43/browser_final.log`。iPad 手势/压感属于指针模拟，**非物理设备验收**。
- 新增所有数学及 Schema 负面测试由 CI 运行，涵盖无效定义域、超范围输入、非法状态、来源漂移、覆盖矩阵计数和学生端剧透。
- 真实日志目录：`evaluations/results/2026-11-09-kb-batch43/`，关键文件 `targeted_final.log`、`mac_check_final.log`、`browser_final.log`。
- `mac_check.sh` 会刷新两份旧日期 JSON 的生成时间戳；该变化是非语义漂移，应恢复原本分支文件，不混入 Batch43 代码提交。

## 4. 严格未完成门槛与下一批

- 未获得任何真实数学教师审核签字；新 24 篇均非正式学生课程。原有 **287 篇历史深度草案**与新增独立待审稿分开统计，不能相加冒充官方批准课程。
- 未有官方课程分母 / 条款逐项归属认证；历史 **538 条未形式认证证明步骤**、**10 项待裁决冲突**、**12 个仅旧关联的编辑目标**没有被本批自动解决。教师 APPROVED=0，学生正式深度发布=0。
- 下一批优先依据真正的课标 PDF 重核必修/选择性必修原子与未编号活动，并补齐剩余 **144** 项无直接编辑稿的课程候选；按结构校对 12 条旧关联、独立证明步骤/反例与定理前提；继续 K08 权限与未见题检索基线。所有 PR 保持 Draft，直到真正课程完整性、数学与教师审核门槛达到。

**验收声明**：本批确有 24 篇原创待审稿 + 24 类精确有限计算工具 + 审核门禁与高风险平移缺陷修复，并完整执行 Mac 测试；但这些结果不能替代数学普遍性证明、官方课程条款验证、真实教师审核或真实学生学习成效。
