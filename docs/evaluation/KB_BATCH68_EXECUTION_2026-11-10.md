# STEM Mentor — Batch68 Mac-only 版本化执行与审查报告（2026-11-10）

## 1. 真实性与范围

- 项目 `YOUessi/stem-mentor`，父任务 #17，子任务 #18–#27。
- 本批实际开发/测试设备：已授权的 MacBook Air，独立工作树 `/Users/youtang/Documents/文件/stem-mentor-kb-batch68`，分支 `feat/kb-batch68-atomic-counterpart-proof-gates`。
- 开发基线：Batch67 PR #92，远端 HEAD `7b254ac05fbb629f441b6c790f3a233eb2e266f3`，通过验收的树 `9f26b79f4c00a751d52b1d4ec8a11ef81a39b0fa`。
- 本批原始 Mac 内容代码提交：`9baa6e2fce5e80bf44179598e3ea956df08b1d1a`；后续报告/日志证据提交另见本分支 Git 历史。
- Mac 主仓11项已有未提交修改不动；不使用 Tang；不使用真实学生数据、不上传原版课标全文、不调用真实模型API、不合并main、不强制推送。

## 2. K00/K01 来源、原子假设与审核

从内部62项临时拆分假设选20项二级候选；逐项关联课程标准页码/行号/来源上下文SHA和对应31篇父级数学范围草案。20个候选中19项标注必修、1项标注选修B；仍有42个临时拆分假设未建立本批逐项课程对应稿。使用 `docs/evaluation/KB_BATCH68_CANDIDATE_LINK_MATRIX.json` 和 `scripts/build_kb_batch68_counterparts.py --check` 回放检查。

警告：**428个启发式条款起点不是428个官方知识原子；62项内部拆分也不是官方课程分母。七条课程轨道正式知识原子总数和覆盖率仍全部为 null。** 全页教师原子化审核0/61；第35页图示等仍需独立视觉审查。所有稿件 `REVIEW_PENDING`，数学论证 `NOT_FORMALLY_CERTIFIED`，教师侧 `TEACHER_ONLY`，正式学生发布0，教师批准0。

## 3. K02–K06 原创深度教学与题族

本批20份原创教师侧暂定原子讲义、40道受控例题及解析、60条分步数学说明、20组失效反例及典型错因、60条三级提示、40项近/远迁移，以及先修建议。内容位于 `knowledge/editorial_review/kb_batch68_counterpart_lessons.json`，生成审核稿 `docs/evaluation/KB_BATCH68_COUNTERPART_TEACHER_REVIEW.md`；源作者TSV和主题提示TSV可重放生成且保留SHA。

内容涉及集合成员与子集、双向包含判等及其他跨主题条件边界；数值见证与分步说明不是一般定理证明。教师解答不得直接进入学生独立挑战。

## 4. K07/K08 数学与Agent的边界

- 20项精确整数/`Fraction`（部分有受控 SymPy）有限实例见证，针对定义域、零分母、参数退化、严格不等号及概率不等可能等进行负例拒绝；限于受控算例，不能自动认证通用命题或自由学生步骤。
- 20项未批准内容的独立非空模拟索引检索防泄漏，确保未批准教师稿无法充当学生端授权证据；此项并非线上模型API安全率。
- 现存538条未形式认证证明步骤、10组未裁决冲突均未因有限测试自动消失。

## 5. Mac 可重放执行记录（最终成功批次）

原始日志及退出码均保存于 `evaluations/results/2026-11-10-kb-batch68/`：

| 验收项 | 实测结果 | 文件 |
| --- | --- | --- |
| Batch68 专项pytest | **210 passed，0 failed**（正式提交前重放仍210 passed） | `incremental.log`、`post_commit_smoke.log`、对应 .exit |
| Python 全量pytest | **46,755 passed，0 failed，1第三方依赖弃用警告**，约252.90s | `mac_check.log`、`mac_check.exit=0` |
| Node TAP | **111/111 pass，0 fail** | `mac_check.log` |
| Tutor合成策略 | **33/33** | `mac_check.log` |
| RAG困难负例 / Top3 | **40/40 / 22/22** | `mac_check.log` |
| Chrome/Playwright | 15个合成浏览器脚本通过，浏览器pytest **2 passed**；无真实iPad硬件验证 | `mac_browser_check.log`、`mac_browser_check.exit=0` |
| Mac基线测试前置重放 | **EXIT 0**（同时保留preliminary日志） | `mac_check_preliminary.*`, `mac_browser_check_preliminary.*` |

Python全量的46,755已包括210项专项，不做重复相加；浏览器脚本为合成场景，不能当作物理设备认证。审计输出不构成真实教师或官方签核。

## 6. 风险、失败及下一整批

本批原始测试与浏览器日志均保存成功，最终退出码为0；没有观察到最终冻结版本的失败回归。第三方依赖产生1条弃用警告。若后续CI失败，需逐条保留失败日志并修复后重放。

后续优先：逐项原版课标视觉/全文核对与跨页实质等价证明，正式建立必修/选择性必修/选修A–E可审计原子分母（E属于学校自定方向，不冒充国家强制数）；为未完成的42项拆分候选和真正缺口继续批量补全完整原创讲义/题族；针对历史538步骤与10冲突提高一般证明与条件验证覆盖；完成真实教师审核，再推进安全索引及冻结API对照评测。维持所有未知量为未知，严禁自动 APPROVED/学生发布。
