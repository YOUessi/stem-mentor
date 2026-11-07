# STEM Mentor｜KB Batch21 执行与审查报告（2026-11-08，Mac）

## 代码事实源与隔离
- 仓库 `YOUessi/stem-mentor`；本批工作树 `~/Documents/文件/stem-mentor-kb-batch21`；分支 `feat/kb-batch21-elective-gaps-math`。
- 基于 Batch20 的提交 `fa19de4f6b32680181d14293b9b3ab8ce2b238f3`；Draft PR 依次堆叠 #45→#46→本批；未修改/重置 Mac 主仓、未动 Tang。
- 本地测试执行环境：MacBook Air、`.venv` Python 3.13、Node v22.23.1；全量测试日志是验收证据，不等于教师数学审核。
- 本次提交自身的 GitHub SHA 以本批 Draft PR 的 head commit 为准（报告不能自引用自己的 SHA）。

## 本批交付（K00/K01/K05/K06/K07/K08/K09）
按 28 张仍待人工判断的 **editorial** 课标缺口候选，原创增加 **11 篇** REVIEW_PENDING、TEACHER_ONLY 深度草案，分类 **定理 6 / 方法 4 / 概念 1**：

| track | 单元 |
| --- | --- |
| Elective A | e 的级数部分和；一阶微分与余项；正交矩阵等距；非齐次线性方程组秩与相容性 |
| Elective B | 仿射目标凸多边形顶点极值；空间异面/非平行直线最短距离；k-means 的非空簇与局部最优；量纲与单位变换 |
| Elective C | 序数量表与单调重编码的均值边界 |
| Elective D | 整数谐波的公共/最小周期与混叠 |
| Elective E | 一阶仿射差分与不动点 |

11 篇均保存完整结构字段：假设/适用边界、原创推导或合法性论证、**共 22 道教师侧例题**、11 条失效/反例、提示阶梯、错因、近远迁移及先修引用。学生端深度证据检索保持拒绝，正式教师审核保持 0。

增量机器规则：`scripts/build_kb_batch21_lessons.py` 审查工程课程 Track 与 gap 对应，只允许 **话题邻近**，不把它冒充官方逐条相同；`scripts/build_kb_batch21_proof_union.py` 合并历史 451 + 新 23 = **474 条未形式化验证证明步骤**，所有状态 `NOT_FORMALLY_VERIFIED`，并检查历史冻结报告和新内容与真实索引一致。原始 28 个缺口候选全部仍 OPEN：11 个只有新内容话题重叠，剩 17 个无本批重叠。

新增精确运算与边界测试（`backend/tests/test_kb_batch21_gap_math.py`）：有理数有限部分和、二次函数微分余项、线性秩判据、等距变换、顶点最值、空间线距离、k-means 中心、单位转换、序数量表、谐波最小周期、仿射差分；覆盖输入条件失效、教师伪签名、越权可见性、错误课程映射、审核队列伪造及不一致来源的拒绝路径。**这些有限 oracle 不证明自然语言完整定理或学生自由步骤。**

## 版本化内容与验收
- 源输入：`curriculum/highschool_math/author_draft_batch21.json`；可复现内容：`knowledge/deep/v1/elective_gap_batch21.json`。
- 课标缺口审计：`docs/evaluation/KB_BATCH21_EDITORIAL_GAP_OVERLAPS.json`；证明步骤联合审计：`docs/evaluation/KB_BATCH21_PROOF_REVIEW_UNION.json`。
- 回归修复：历史 Batch02/07/09/10/11/12/13/14/15/16/17 审计与全量索引之间，区分**冻结历史分母**与**最新 235 草案动态分母**，避免把历史 224/451 的证据文档改写成新批凭空验证。新增失败闭合的证明队列来源一致性检查。
- 首轮 Python 全量：**18847 passed，5 failed**；失败原因主要为冻结旧快照与新 11 篇共用动态总数，已修复。
- 中途目标回归：**4706 passed，0 failed**（新增 3 条审计抗篡改检查后）。
- 最终 Python 全量：**18855 passed，0 failed，1 个第三方 anyio/Starlette deprecation warning，65.52 秒，EXIT=0**；证据 `evaluations/results/2026-11-08-kb-batch21/python-full-final.log`。
- CI Python 预检：**32/32 通过**，日志 `evaluations/results/2026-11-08-kb-batch21/ci-python-gates.log`。
- Node：**111 passed / 0 failed**，日志 `evaluations/results/2026-11-08-kb-batch21/node.log`。
- 浏览器：`scripts/mac_browser_check.sh`，**EXIT=0**，多组 Chrome 移动/平板/桌面与数值边界、交互回归，日志 `evaluations/results/2026-11-08-kb-batch21/browser.log`。
- 全部结构/快照检查 `build_kb_batch21_lessons.py --check`、`build_kb_batch21_proof_union.py --check` 通过；无真实学生数据上传。

## 保守课程覆盖与发布边界
- 工程映射节点：**161**（不是官方课程原子完整分母）；深度草案：由 **224→235**。前一批报告的正式官方原子分母仍未知，**official_atomic_denominator=null**。
- 课标来源编号位置与未编号方向不能直接累计为完整官方分母；需继续 K00 独立逐项课标比对和教师复核。
- 教师 APPROVED：**0**；整篇证明形式化认证：**0**；学生可用深度知识：**0**；学生自由文字证明已验证：**0**。
- 28 个 editorial 缺口候选未关闭，10 份旧版冲突仍未裁决，474 条自然语言证明步骤待风险分层和教师审阅。

## 下一批依赖与风险
1. **K00/K01** 按课标逐条定义必修、选择性必修、选修 A–E 的机器可审计原子分母（明确未编号与开放方向、来源页证据、是否真正缺失），避免“427 张任务卡就是 427 个官方知识点”的谬误。
2. **K07** 审查新增 23 条证明步骤，历史 451 风险队列按 P0 优先处理；可用符号证据只给出所覆盖子命题，剩余保持未验证。
3. **K05/K06** 对 28 缺口中剩余 17 个继续做严谨原创讲义、题族/错解/分层提示，不为填数而虚构课标映射。
4. **K08/K09** 独立检验未经批准的检索拒绝、学生防剧透及 API 错误归因；安排真实教师审校，禁止机器人自签 APPROVED。

参见 GitHub Issues #17–#27 与本批 stacked Draft PR；以 PR head SHA 和本文件列出的真实日志作为提交事实。
