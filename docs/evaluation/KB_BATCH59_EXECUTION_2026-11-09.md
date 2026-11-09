# STEM Mentor｜Batch59 Mac 执行与验收记录（2026-11-09）

## 运行边界与 Git 事实
- 唯一开发/内容环境：授权 `YOUTangdeMacBook-Air.local`，独立 worktree `~/Documents/文件/stem-mentor-kb-batch59`；未使用 Tang、未改动主仓未提交修改、未合并 main、无强推。
- 工作分支：`feat/kb-batch59-selective-source-guards`；基线 Batch58 PR #83 的 `17a32f909b6e45e449dd883ec13ab9f509e0b866`。
- **数学、来源审计与测评源码提交 SHA**：`797e478efcd4a12026f4203f2890c0aa1c376970`。包含本报告的后续文档提交及远端 PR HEAD 以 GitHub 实际状态为准。所有交付均保持 Draft，不能据此标记正式验收。
- 官方课标：教育部《普通高中数学课程标准（2017年版2020年修订）》，仅在授权 Mac 使用本地固定原 PDF `/private/tmp/stem-mentor-official-math-2020-batch51.pdf`；原始 PDF SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。没有提交 PDF 或其完整版权页文本。

## K00/K01｜课标来源审计、课程范围与可重放门禁
- 逐段定位印刷**第37–50页（14页）**，新增 **108 条非去重课标来源片段指针**（CONTENT 60、TEACHING_GUIDANCE 28、ACHIEVEMENT_REQUIREMENT 13、OPTIONAL_STARRED 5、ACTIVITY_REQUIREMENT 1、TRACK_BOUNDARY 1）。包括数列、导数、空间向量、解析几何、圆锥曲线、计数与概率统计、研究性活动；星标选学不冒充全国统一必授。
- 从 Batch56 的52、Batch57 的78增加到**238条非去重来源定位记录**，部分定位累计**36/61页**（印刷15–50页），**完整逐页教师原子化页数仍为0**。未覆盖的25页包含13–14和51–73，图像/建模证据仍待单独核实。
- 单独建立**42条未获得独立能力达标证据**的学业/教学/活动来源要求审查队列；它们不能因不是内容原子而从学业要求覆盖指标消失。与 Batch58 前序能力队列的去重等价尚未认证，不能直接相加为官方独立能力分母。
- 所有源指针包含来源页、PDFKit行范围、完整 PDF SHA、页 SHA、片段 SHA、原创中文释义、条件门禁和课标轨道；只提供同页课程编辑**检索线索**，不证明数学等价、课程内容覆盖或教师审核。新增 `scripts/build_kb_batch59_selective_source_review.py`、源位置 TSV、PDFKit 片段指纹 JSON、机读/人工 Markdown 审计。源 PDF 被独立重读校验，锁定61页原有指纹和本轮108片段 SHA。CI不内置版权 PDF，因此仅校验已版本化哈希审计与生成一致性。
- 七轨的**官方全量知识原子分母均保持 `null`**；313只是项目编辑候选，不是课标原子个数。10组数学冲突仍未裁决，538条历史证明步骤未获得形式认证。全程拒绝伪造教师签字、已审校、学生发布和考试必修属性。

## K06/K07｜原创教师测评和数学条件验证
- 针对本批**13项学业要求与1项活动要求**分别制作**14份原创、仅教师可见的独立测评草案**，每份有题目、前提、至少三步带依据的讲解、典型错法、反例/失效条件、三级提示、近迁移、远迁移、评分量规、来源关联 ID 与未审校状态。源码为 `curriculum/highschool_math/kb_batch59_selective_assessment_drafts.json`，生成 `KB_BATCH59_SELECTIVE_ASSESSMENTS.md` 及跨表 JSON。
- 建立**12类有限精确数学见证**，使用 `Fraction`/有界整数枚举：等差和、等比和（`q=1` 分支）、仿射复合平方导数、空间基底唯一坐标（行列式非零）、方向向量平行/垂直与斜率、椭圆参数退化、组合数、超几何概率、两假设贝叶斯及正证据前提、Pearson `r²`、一元最小二乘、2×2 卡方统计。
- 严格区分数值实例校验与一般定理证明，拒绝零方差、零分母、共线基底、非整数计数、无效概率/组合参数及额外伪审核字段；未授权内容不进入学生端教师完整解答。各稿均 `REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED`；**14份草案均未获得真实教师审核**，42条能力/教学/活动要求仍 **UNMAPPED**，不能因有草案而算达标。
- 学生自由证明、真实学生测评、外部模型 API 冻结对照和真正教师审校本批都没有完成；不上传真实学生数据。

## 测试环境与可重放验收（Mac 真执行）
- `PYTHONPATH=backend:. .venv/bin/python -m pytest -q backend/tests/test_kb_batch59_source_and_exact_guards.py backend/tests/test_kb_batch59_selective_assessments.py`：**274 passed，0 failed**（日志 `evaluations/results/2026-11-09-kb-batch59/incremental.log`）。
- `scripts/mac_check.sh`：**EXIT=0**；其中 Python 全量 **44,012 passed，0 failed，1条第三方警告**（包含本批274项，不重复累计），Node **111/111 passed**；Tutor策略 **33/33**、RAG困难负例 **40/40**、Top3 **22/22**。完整日志 `mac_check.log` 与 `mac_check.exit`。
- `scripts/mac_browser_check.sh`：**EXIT=0**，Chrome/Playwright 15个脚本、浏览器 pytest **2 passed**。使用合成库、CDP模拟，**不是实体 iPad 验收**；日志 `mac_browser.log` 与 `mac_browser.exit`。
- Mac 本地原 PDF 独立复验：`python scripts/build_kb_batch59_selective_source_review.py --check --verify-source-pdf /private/tmp/stem-mentor-official-math-2020-batch51.pdf --source-dir /private/tmp` **PASS**（61页页级哈希+108段来源哈希），`author_kb_batch59_selective_assessments.py --check` **PASS**，日志 `source_attestation.log`。
- 首次独立运行新增 pytest 时未设置 `PYTHONPATH`，发生**2项模块导入收集错误**（见 `incremental_first_import_failure.log`），修正运行环境而非修改数学逻辑后复测 **274/274 通过**。另一次全量检查只改变历史静态测试结果中的 `generated_at` 时间戳，已在本独立 worktree 恢复原值以避免无关变更。
- 工作流 `.github/workflows/ci.yml` 和 `scripts/mac_check.sh` 已加入 B59 的生成一致性门禁；正式 GitHub CI 检查及远端 HEAD 必须在 PR 创建后单独核实。

## 风险与下一批依赖（不得自动销项）
1. K00优先继续印刷51–73页（包括选修 A–E）、补印刷13–14页及第35页图像证据；核查真实课程文本与标题/选修轨道，逐项完成非编号要求、跨页数学等价去重，**只在61页全量教师审查后**建立每轨可机器审计的正式原子分母。
2. K01/K09按知识类型分别做字段审查，教师对14项测评量规、历史内容逐条签名；学生正式深度发布依旧0，审批必须与机器验证严格分离。
3. K07继续审查10组未裁决数学内容冲突及538条历史未形式认证证明步骤，逐项维护前提、边界、反例和真实教师复核。
4. K08/K09继承 Batch58 混合已签名/未批准语料检索回归，扩大真实撤销/提示注入/题族迁移覆盖，后续开展合法授权模型 API 的冻结对照，分别报告数学正确率、引用、延迟、成本与拒答。
5. 在 K00 官方原子分母确认后计算缺失深度内容、题族和先修约束；有缺口再整批补齐，不把238条来源指针、14篇测评草案、313个工程目标或71画板当作官方全量覆盖。
