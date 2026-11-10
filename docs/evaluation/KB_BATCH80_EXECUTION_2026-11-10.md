# STEM Mentor｜Batch80 执行与验证报告（2026-11-10）

> 源码开发、内容生产、验证均在授权 MacBook Air 独立 worktree `~/Documents/文件/stem-mentor-kb-batch80`；基线为 Batch79 GitHub commit `7a5768a1c2fc1bd5d574d73c5933e4a772ac442c`。Mac 主仓原有 11 项未提交改动不纳入本分支。此报告记录候选任务，不宣称全量官方知识原子、教师批准或一般定理形式认证。

## 本批范围：K00 + K01 + K07 + K08 + K09

- K00：在版本化 JSON 中明确 **428 项来源锚点待课程原子化义务**，每一项保留页码、PDFKit 行号、来源 SHA、父来源分区、课程轨道、审核状态；428 是审核队列的分母，**不是课程官方知识原子分母**。
- 七轨机器审计（来源锚点）：必修 142，选择性必修 101，选修 A 69、B 70、C 29、D 17、E 0；选修 E 尚需按学校实际开设课程另建分母，且选修总论不能强行归入 A–E。
- 保留 61 页来源区域、484 页内文本来源区间、56 个非锚定编辑分诊、60 个子片段、26 个局部主题候选；各阶段不同层级，禁止直接相加成课程知识原子数。
- K07：538 条历史证明步骤逐条保留 ID/原始 SHA、优先级、审核链接；其中风险 P0 为 127 条，已有待审教师卡链接 36 条（本批新增 8 条），P0 尚无教师卡 91 条。10 组数学冲突仍未裁决。
- K07/K06：8 份原创高风险数学论证教师草案（每篇含完整假设、3 段论证、2 道教师侧例题、典型错误、失效反例、3 级提示、近/远迁移），合计 16 道例题、24 段论证、8 组反例、24 条提示、16 项迁移。
- 数学主题：对数积法则的实数域条件、二次函数配方合法前提、绝对值三角不等式等号条件、分步计数乘法原理、切线微分近似的前提、向量夹角非零条件、全概率公式要求事件分割、二倍角单位圆恒等式。
- 8 类受限精确整数/有理数验证各有有效见证与无效条件拒绝；不做学生自然语言完整证明判定，不得把有限实例的测试通过标为定理已形式认证。
- K08：8 份 `TEACHER_ONLY` 卡在存在已批准非空检索索引的测试环境下不可通过学生检索泄漏完整教师解答。
- K01：修复 `scripts/build_kb_batch78_scope_graph.py` 的 Python 链式不等式审核门禁缺陷：原 `x!=y!=z!=w!=0` 并非「四个值都为零」，在四源审查计数全被伪造为相同非零值时可能误放行；改为对四个独立来源逐个要求 `type(value) is int and value == 0`，阻止布尔型、浮点 0.0、字符串、缺失值和相同值伪造。补充 42 项针对全部来源的参数化负面回归。

## 源码、数据与版本化证据

- 审核队列生成器：`scripts/build_kb_batch80_review_queue.py`。
- 原创教师草案生成与强约束：`scripts/build_kb_batch80_eight_cards.py`。
- 受限精确数学检查：`backend/app/kb_batch80_math.py`。
- 生成物：`curriculum/highschool_math/kb_batch80_review_queue.json`、`docs/evaluation/KB_BATCH80_PROOF_QUEUE.json`、`knowledge/editorial_review/kb_batch80_eight_proof_guard_cards.json`。
- 增量回归：`backend/tests/test_kb_batch80_scope_and_proof.py` 和 `backend/tests/test_kb_batch78_scope_graph.py`。
- 集成 CI：`.github/workflows/ci.yml`、`scripts/mac_check.sh` 的构建器 `--check` 及批量测试调用。
- 可重跑原始证据：`evaluations/results/2026-11-10-kb-batch80/`；原始 Batch80 专项在门禁修复前为 `2401 passed`；修复后两个专项文件组合为 `3236 passed, 0 failed`（新加入42项）。

## 完整验证与失败案例

门禁缺陷发现时仅静态定位，不能将其登记为教师审核违规已实际发生。已在 Mac 用参数化负例重放了四源单项伪造、四源全等伪造（同为 1/-1/True/"0"/None/0.0）、缺失字段，均被正确拒绝。

- Mac 专项：`batch80_plus_review_gate.log`，3236 passed；`batch80_plus_review_gate.exit=0`。
- 完整 Mac 检查：`mac_full_after_gate.exit=0`，Python **54,715 passed、5 skipped、0 failed（1条第三方依赖弃用警告）**；Node **111/111通过**；模拟 Tutor 策略 **33/33**，RAG困难负例 **40/40**、Top3 **22/22**。完整日志 `mac_full_after_gate.log`。
- 浏览器检查：`mac_browser_after_gate.exit=0`，15 个 Chrome/Playwright 检查脚本通过，浏览器 pytest **2 passed**；包含页面交互、三档响应式窗口、iPad 指针模拟（不代表真机验证）、无外部请求/学生真实数据写入。原始日志 `mac_browser_after_gate.log`。
- 旧测试冻结证据：门禁修复前 Mac Python `54673 passed, 5 skipped`，只能作为历史中间结果，不能冒充修复后最终结果。
- **修复前失败案例**：四份来源的 `teacher_full_page_reviews` 同时伪造为数字 1 时链式不等式返回 False，旧代码不能拒绝；修复代码与负面测试确保此类输入抛出 `ValueError`。
- 教师批准 0、全页教师原子化 0/61、正式学生发布 0、官方七轨知识原子分母全部未知；这些是不可绕过的发布阻断。

## 下批优先级

1. K00：真正逐页把428个候选审核义务拆分成「课程数学原子 / 课程能力 / 活动 / 跨页重复 / 非课程内容」并做数学等价去重；建立机器可审计的**官方**分母（以真实教师核对及课程来源为准），尤其单列学校选修 E。
2. K07：继续处理 91 个无审查卡的 P0 历史步骤，独立核实10组数学冲突。所有非形式验证仍需教师审核。
3. K02–K06：从已定位官方范围扩展完整原创教师讲义、题族、必要证明与独立精确数学负例，不以工程目录和审核卡总量冒充全量覆盖。
4. K08/K09：复核已批准索引边界、学生自由解题步骤的 `UNSUPPORTED`/未验证返回、真实教师审核及正式发布门禁。

本批 Draft PR 保持 Draft，不合并 main。实际提交 SHA、最终测试数字及 GitHub CI 运行记录以 PR/Issues 的后续验收回执为准。

## 冻结源码 SHA 与远端CI验收回执

- 本批 Mac 源码+数学内容+原始测试证据提交：`2e1dc8062c27f1c681ea2acb9be542e29741255c`；对应 Git Tree：`13a27ba65db4589167e213cf9969bf46b0edf5a1`，26个变更文件。正常 Git push 成功，GitHub 原生接口已回读同SHA Commit及关键源码。
- 对上述源码提交的 GitHub Actions：`https://github.com/YOUessi/stem-mentor/actions/runs/42811308968`，Completed / Success；test job 138/138个步骤成功，0失败、0跳过。
- 上述SHA锚定冻结的源码和原始日志，不用对本报告后续记录补充产生的文档提交反向重写历史代码SHA。CI成功只证明工程及受限数学实例检查通过，未通过教师审校、一般形式证明或学生正式发布门禁。
