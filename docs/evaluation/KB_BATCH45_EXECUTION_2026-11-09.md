# STEM Mentor｜Batch45 Mac 实际开发、数学审查、回归证据（2026-11-09）

## 1. 源码事实源及开发范围

- 唯一编码、数学内容生产和测试机器：授权 `YOUTangdeMacBook-Air.local`；独立 worktree `/Users/youtang/Documents/文件/stem-mentor-kb-batch45`；分支 `feat/kb-batch45-core-geometry-probability`，基于 Batch44 GitHub HEAD `008f893eb55666cf93f596b239cf8c16b633c0bc`。
- Draft PR #70：https://github.com/YOUessi/stem-mentor/pull/70。源代码实际 Mac 提交 `d5637d52dd5a727a385ba300a18eb14150fed6e1`，tree `5aaa32acf696a0d6a5d1e270aa3e644ed8e79430`；最终日志证据提交与 GitHub Actions 运行以远端回读为准。
- Mac 原主仓 11 项未提交工作原样保留；没有使用 Tang、修改主仓、强推或合并 main。不包含真实学生数据、版权教材全文或虚构教师批准。
- 本批以已冻结的**项目自编**编辑目标为内容来源，并没有重新核定课标全量知识原子；不得以项目编辑目标数量冒充官方课标分母。

## 2. K00/K01/K02–K04/K06：24 篇原创必修待审教学稿

- 本批 `knowledge/editorial_review/kb_batch45_core_depth.jsonl` 新增 24 篇原创审校稿；其中三角函数、零点及二分法 7 篇，平面向量/复数/空间几何 8 篇，概率统计及抽样 9 篇。
- 每篇含数学陈述、适用域及前提、先修依赖、三步有依据论证、错误主张与具体反例、两道含步骤及验证的**教师侧**例题、三级针对性提示、近远迁移。合计 48 教师例题、24 具体反例、72 层提示、48 个迁移任务。定义、方法只要求符合实际的合法性论证；不得为所有内容假造“形式证明”。
- 课程目标逐项匹配并冻结来源 SHA / 源行及知识内容 SHA：`KB_BATCH45_CORE_DEPTH_AUDIT.json`、`KB_BATCH45_CORE_DEPTH_MANUSCRIPTS.md`、`KB_BATCH45_PROJECT_SCOPE_OVERLAY.json`、`KB_BATCH45_PROJECT_SCOPE_GAPS.md`。新增稿均是 `REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED`，不自动 APPROVED。
- 更新 313 项**非官方**项目目标矩阵：**201 有直接待审稿 + 12 仅旧非等价关联 + 100 无直接稿**；必修 125 目标/91 待审稿关联/34 缺稿，选择性必修 92/26/66；选修 A–E 保持原状态。七轨道正式课标分母及覆盖率继续 `null`。

## 3. K07：24 类精确有限实例校验及独立数学纠错

- 受控计算涵盖三角周期/加减角/分母零点、零点异号与二分误差、向量基底/内积、复数除法、立体几何退化、有限样本空间/事件逻辑、古典概率前提、无放回均匀抽样、比例分层整数分配与描述性方差。
- 每类具有合法数据、非法数学前提、缺失/额外字段及任意输入不认证负例；使用有限整数、精确 Fraction、明确几何配置，部分通过 SymPy 独立三角实例核验。对所有返回固定拒绝 `general_theorem_certified`、`teacher_approved`、`student_freeform_step_verified` 与 `student_publishable` 权限。
- **实际发现并修改两项数学语义漏洞**：(1) 端点异号最多保证连续函数存在零点，原状态名 `ROOT_EXISTS_NOT_UNIQUE` 可能误导为“已经证明不唯一”，现改成 `ROOT_EXISTS_UNIQUENESS_UNDETERMINED`，并分别测单调函数及多零点三次函数；(2) 每次观测允许 H/T 并不保证 2^n 联合序列都可能（完全相关观测仅 HH/TT），现必须声明 `all_sequences_possible=true`，否则拒绝返回 2^n。声明仍只属于调用前提，不证明实验本身满足。
- 初轮专项曾为 **411 passed / 4 failed**：其中三项是反例/错因文本不能达到质量 Schema，另一项是测试自身误判多项式 `x(x²−1)` 的端点异号；均已纠正。后续严格条件改动后一度因生成审计未更新出现 **415 passed / 1 failed**，通过重新生成冻结 JSON 审计后最终 **416 passed / 0 failed**。先前一次完整脚本遗留 `exit=2`；本轮完整重跑确认语法检查通过、脚本 `exit=0`。绝不把首次失败隐藏成未发生。
- 这些实例与穷举不能证明一般定理，不能认证未被支持的学生自由推理。历史 538 条未认证证明步骤和 10 组历史冲突尚未裁决。

## 4. K08/K09：真实 Agent 权限回归及 Mac 完整测试

- 对全部 24 篇新稿实际调用现有 `student_evidence_lookup` 与 `draft_next_question` 进行负面测试：学生证据为空、模型不调用、完整教师答案不泄漏；不是仅测试 JSON 投影，也不冒充线上模型评测。
- 本批专项 **416 passed / 0 failed**；`mac_check.sh` 全量脚本 **EXIT=0**，Python **39,821 passed / 0 failed / 1 第三方弃用警告**，Node **111/111 passed**；教学策略 **33/33**，困难检索负例 **40/40** 和 Top3 **22/22**。（真实数目以附带原始日志为准。）
- 浏览器 `mac_browser_check.sh` 已独立重跑 **EXIT=0**：Chrome/Playwright **15 个脚本通过**（多个响应式分辨率、实验室交互、iPad 笔触与缩放模拟）、浏览器 pytest **2 passed / 0 failed**；使用临时合成 SQLite、无学生上传或外部请求。iPad 仅为浏览器指针模拟，**不是实体 iPad 设备认证**。
- 日志：`evaluations/results/2026-11-09-kb-batch45/mac_check_full.log`、`mac_check.exit`、`mac_browser_full.log`、`mac_browser.exit`，及本项目已有的审计 JSON。源代码提交已取得 GitHub Actions #42513746728 `completed/success`；最终证据提交对应的 CI 仍需远端单独确认。

## 5. 未完成门槛与后续开发链

1. 完成仍缺的 **34 项必修 + 66 项选择性必修**项目候选稿；须先查重复和实际官方条款归属；不得提前给出官方课标覆盖率。
2. 继续逐页、逐条、含未编号学习要求核定必修/选择性必修/选修 A–E 正式原子分母；项目 313 自编候选不能作为官方分母。
3. 核查 12 项仅旧稿关联的数学范围，并分级处理 538 条历史证明步骤和 10 组冲突；条件有限见证不替代形式证明或真实教师审查。
4. 在教师有源可验的签署审批前，所有新稿保持 `REVIEW_PENDING`，`teacher_approved=0`、`student_published=0`；持续维护真实 RAG/API 防剧透、拒答与条件前提门禁。Draft PR 保持 Open，不合并 main。

**本批工程验收不等于全量数学教育内容验收，不代表官方课标全覆盖。**
