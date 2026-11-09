# STEM Mentor｜Batch52 K00 高风险未编号要求逐项拆分与待核关联（2026-11-09）

## 环境与变更边界

- **唯一开发/测试设备：MacBook Air** `YOUTangdeMacBook-Air.local`，独立 worktree `~/Documents/文件/stem-mentor-kb-batch52`，分支 `feat/kb-batch52-requirement-coverage`；父提交 Batch51 `ceafd4606511712901fa001da125d21264f8cc30`（Draft PR #76）。
- Mac 主仓 `~/Documents/文件/stem-mentor` 原有 11 项未提交修改均不触碰；不使用 Tang，不强推、不合并 main。
- 原始课标：教育部《普通高中数学课程标准（2017年版2020年修订）》，Mac 本地 PDF 原件，SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。本轮使用 PDFKit 实际重新查看重点印刷页 34、35、41、50、65；全部 61 页 PDFKit 指纹来自 Batch51 已提交的来源记录，PDF原文和图像均未上传。
- **状态边界**：这些是对课标要求的原创编辑拆分候选，非官方逐条认证原子、非完整讲义、非形式证明、非教师批准。旧 313 项项目编辑候选仍只代表项目内部集合，不能充作全量高中数学官方分母。

## K00：跨四个关键页面的原创要求候选交叉审计

| 印刷页 | 来源区块 | 轨道 | 逐条原创改写候选 |
|---:|---|---|---:|
| 34 | 必修概率统计学业要求 + 数学建模导语 | COMPULSORY | 8 |
| 41 | 选择性必修数列、导数的学业要求及解析几何导语 | SELECTIVE_COMPULSORY | 8 |
| 50 | 选择性必修数学建模/探究课题研究要求 | SELECTIVE_COMPULSORY | 5 |
| 65 | 选修C数学逻辑、证明与应用模型 | ELECTIVE_C | 7 |
| **合计** | 来源第34、41、50、65页 | 三轨道 | **28** |

- 本轮逐项定义原创教学目标、内容类型（概念/方法/活动/定理范围等）、源文件 SHA256、PDFKit 页文本 SHA256、印刷页、PDF 索引、课程轨道和来源区块。
- 28 条中，**19 条**与本页原有编辑候选有「主题相关」链接，但**绝不认定数学范围等价**；**9 条**未找到同页项目编辑候选链接，这并不证明它们是全库真正缺口，仍须跨页去重和旧稿逐条核对。
- 原有 Batch51 的第35页 **7 条建模拆分候选保持独立**，没有在本批28条中重复计数。原始313编辑候选、317编号标记出现次数、23条D/E提纲均保持独立统计，不能相加得出官方知识原子分母。
- K00 官方知识原子分母继续 **必修=null、选择性必修=null、选修A–E各=null**；教师已批准=0，学生正式深度发布=0。
- 特别纠偏：印刷第41页的“解析几何承接导语”是结构性提示，不是可以直接宣称独立新定理的课标原子；第65页的经济/社会模型示例属于选修范围，不能提升为全国必修。

## K01/K09：工程实现与审查门禁

新增 `scripts/build_kb_batch52_critical_requirement_crosswalk.py` 及机器审计件 `KB_BATCH52_CRITICAL_SOURCE_CROSSWALK.json`、人读对照 `KB_BATCH52_CRITICAL_SOURCE_CROSSWALK.md`，并加入 `.github/workflows/ci.yml` 与 `scripts/mac_check.sh` 的 `--check` 门禁。

验证器拒绝 PDF 原件 SHA漂移、PDFKit缺页/页码/指纹篡改、未经审查的页面认证、重复候选ID、孤儿/跨课程轨道/错页的旧候选关系、伪造教师批准/学生发布、把313编辑候选或编号次数误标为正式分母。每一条与旧稿的连接状态都是 `RELATED_SCOPE_UNVERIFIED`，不能自动作为权威学生证据。

独立有限真值表还检验选修C基础逻辑实例：经典二值命题的排中律、矛盾律与逆否等价；逆命题或否命题不能偷换为逆否命题。其作用仅是有限布尔值样例核验，**不认证任意逻辑系统一般定理或自然语言自由证明**。

本批实际新增 **89 个专项 pytest 回归用例**，正反覆盖28个候选、四页指纹、关系完整性、假官方分母、伪教师审批、学生发布和基础命题逻辑反例。

## 真实执行与问题修复

- 构建/复现：`.venv/bin/python scripts/build_kb_batch52_critical_requirement_crosswalk.py` 与 `--check` 均成功。
- 第一次执行出现一次实际实现异常：把上游 `track_evidence`（列表）错误当作字典调用 `.get`，抛出 `AttributeError`；改为检查 `review_gate.official_atomic_knowledge_denominator` 及逐轨 `official_atomic_denominator` 后重新执行成功。
- 增量测试：`89 passed / 0 failed`，真实日志 `evaluations/results/2026-11-09-kb-batch52/incremental.log`。
- **Mac 全量测试已实际执行通过**：Python `42,707 passed / 0 failed / 1 Starlette/AnyIO 第三方弃用警告`（包含本批新增的89个专项测试，勿与增量结果相加）；Node `111/111 passed`、Tutor 策略 `33/33 passed`、RAG 困难负例 `40/40` 与 Top3 `22/22`。`mac_check.exit=0`；原始输出：`evaluations/results/2026-11-09-kb-batch52/mac_check_full.log`。
- **Mac Chrome/Playwright 全套已实际执行通过**：15个浏览器脚本（数学画板、极端值、页面、iPad手势模拟）全部成功，浏览器 pytest `2 passed / 0 failed`，`mac_browser.exit=0`；日志：`evaluations/results/2026-11-09-kb-batch52/mac_browser_full.log`。使用合成数据库，iPad触控/压感为CDP指针模拟，**不是实体iPad验收**。
- GitHub PR/远端commit/Actions：将在远端推送并复核后单独追加回执，不预先伪称CI通过。

## 下一批与阻断

1. K00：从印刷第13–73页的61个课程内容页进一步覆盖所有编号/未编号要求、活动/学业要求及图形，优先解决本批9条“同页未链接”的跨页去重；再冻结经过教研审查的七轨道官方知识原子分母。
2. K01–K06：将真实缺口连接到原创完整讲义、形式准确的定义/定理/反例/题族/迁移，而非仅建立目录或候选数。
3. K07：继续处理历史538条未形式认证证明步骤与10组冲突，逐前提审查；本批真值表实例不能取代一般证明。
4. K08/K09：0份教师批准意味着正式学生内容索引仍然不得上线；真实授权模型 API 的引用、数学正确率、泄露率、拒答率、成本和 P95 评估尚待执行。

## GitHub 源码与首轮 CI 验收回执

- Batch52 真实源代码、审计、测试日志完整提交：`baa04978a4cec4ebf7cede919fbe951b88788d24`，Git Tree `dcb01e9ca0933d9f9d9e5af6a54d02eb43f67798`；12 个变更文件。
- GitHub Draft PR #77：https://github.com/YOUessi/stem-mentor/pull/77，基线 Batch51 #76；保留原有 main，不合并。
- 此源码 SHA 触发的 GitHub Actions #42540202153 已核实 `completed/success`：https://github.com/YOUessi/stem-mentor/actions/runs/42540202153；CI 包含本批 source crosswalk `--check`、Python/Node与教学策略回归。
- Mac 本地 worktree 与 GitHub 上脚本、审计JSON、专项测试、报告的 Git Blob SHA 一致；main 仍有既存11项未提交修改，没有被修改或覆盖。
- 本页回执追加本身会形成后续 Git commit；最终 GitHub HEAD 和对应 CI 应以 PR #77 最新回执为准。
