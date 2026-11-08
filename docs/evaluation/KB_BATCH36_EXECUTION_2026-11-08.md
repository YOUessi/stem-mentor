# STEM Mentor｜Batch36 实际执行报告（2026-11-08）

## 开始前的事实核对与开发环境

本轮先通过 GitHub connector 读取总 Issue #17 与 #18–#27、最近 Draft PR #60/#59/#58，核实前序 **49 项新选修教师审核稿**（Batch34 20 + Batch35 29）、**47 条遗留关联**、**287 篇旧深度草案**，以及 K00/K07/K09 的未完成门槛。随后在唯一允许的开发设备 MacBook Air 创建全新的隔离 worktree：`~/Documents/文件/stem-mentor-kb-batch36`、`feat/kb-batch36-crosswalk-condition-audit`。父提交直接从 GitHub 远端的 Batch35 分支 `266fc6d58bcda70919781985d748ea9a644258a6` 获取，父 Git Tree `00d507a0eb8a50bc205a913005155903a30982c7`，无需重写或改动 Mac 主仓 11 项历史未提交修改。Tang 未用于本批任何开发。

## 本批真实工程及内容成果

**K00/K01/K05/K07**：逐项编写 `curriculum/highschool_math/k00_batch36_47_legacy_scope_reviews.tsv` 的 47 条有明确来源 ID 的数学审核提示，各条均有实际适用前提、具体未覆盖范围/反例和三类审核标签。其中 **12 条 CLAUSE_UNVERIFIED、27 条 PARTIAL_SCOPE、8 条 CLAIM_MISMATCH**；关联旧讲义实际涉及 **44 个不同原稿**（A16、B12、C9、D7、E3）。8 项数学任务错配不是“数学定理已判错”，而是历史关联不能视作能力/课程等价覆盖。

`scripts/build_kb_batch36_legacy_scope_review.py` 读取固定 SHA 的原 47 条关联、从真实 `knowledge/deep/v1` 读取并检查 **287 篇原草案**，对旧讲义的实际数学内容计算逐篇 SHA256，并将数学前提、反例数量、文件路径、来源版本写入可再生的 `docs/evaluation/KB_BATCH36_47_LEGACY_SCOPE_AUDIT.json`。同时拒绝重复/遗漏课程 ID、未确认来源、被篡改的人工审核种子、伪审批、草稿可见性意外改变等问题。保留 `official_clause_alignment_verified=false`、`mathematical_equivalence_certified=false`，不把本批 47 项范围审查称为 47 项官方知识原子认证。

**K07**：新增 `backend/app/kb_batch36_finite_review.py`，提供 12 类严格字段和数值范围受控的精确实例算子：1/n 的 ε–N 单例、矩阵可乘维度、二阶 Cramer 非奇异、等额期末年金现值、非负归一三角密度、二次函数中值定理单例、二项尾概率、两个不同横坐标的回归斜率、连续二次函数夹值单例、非零直线法向、两点均值和整数节拍 LCM。每类提供一个合法实例和一个非法前提实例，拒绝布尔冒充整数、缺参、多参、超范围数、未知算子。返回 `FINITE_EXACT_CASE_ONLY` 而非 `VERIFIED`，不接收学生任意自由文本证明。

数学推导及关键退化反例见 `docs/evaluation/KB_BATCH36_MATH_SCOPE_AND_FINITE_WITNESSES.md`。

**K09**：为这 47 个具体关联与 12 个数学算子增加 `backend/tests/test_kb_batch36_legacy_scope_review.py`：**245 项专项测试**，涵盖真正旧内容哈希绑定、适用域条件、课程来源、不冒充教师、学生无答案泄露、多种非法输入和伪造记录。所有审计生成内容的 `--check` 已接入 Mac `scripts/mac_check.sh` 与 GitHub `.github/workflows/ci.yml`；完整源码与内容均保持可复现。

## 真实 Mac 验收与失败修复

- 新增专项：**245 passed，0 failed**。最初首次执行新审计脚本时发生了 Pydantic ID 正则反斜杠转义错误，导致课程 ID 无法匹配；修正后重新生成审计文件并完成专项复测。
- 全量 Python（Mac）：**37,672 passed，0 failed，1 个外部依赖弃用 warning**，耗时 136.55s。
- Node：**111/111 passed**；教学策略回归 **33/33**；检索困难负例 **40/40**、Top3 **22/22**。
- Chrome/Playwright 15 个脚本及浏览器 pytest 2 项：**15 个脚本全部 PASS，浏览器 pytest 2 passed，BROWSER_EXIT=0**；使用临时合成数据，iPad 仍是指针模拟。
- 本轮数学工具是精确有理数/整数有限验证，**不能认证全部 theorem**；未经真实教师批准的内容不进入学生端权威索引。
- 部分历史 `evaluations/results/2026-10-15-*.json` 在运行 Mac 回归时被刷新生成时间戳，属于无意义变更，最终提交前在本隔离 worktree 恢复原始文件，不改变历史对照基线。

## 课程真实完成边界

313 个项目自编课标编辑候选（必修125、选择性必修92、选修96）不等于官方全部原子数；七轨道官方分母与正式覆盖率仍为 `null`。原始 61 页都曾首轮查看，但并未逐条完整原子化。此前 47 条历史关联现在 **47/47 有具体数学范围审查材料，0/47 正式认证为课标等价**；另外 49 项选修内容只有单独待审稿，旧 287 篇仍为待审草案。本批新增完整深度讲义 **0**；538 条未形式认证证明步骤与 10 组历史冲突仍待进一步核查，教师 APPROVED 0、学生端深度内容正式发布 0。

## GitHub 提交、CI 和下一批

经完整 Mac 测试的 Batch36 源码提交为 `8f79386ea816afc47372f1dc14e7fda1f1b0c150`，源码 Git Tree 为 `a5e4c116f6653355682e5eb8453c4e5782f18955`。追加本报告与真实测试日志后将独立提交并检查 Mac/GitHub 文件树；Mac HTTPS git push 首次失败，错误是 `Empty reply from server`，必要时经 GitHub 原生 Git 对象接口进行无强推同步。远端 CI 结果只有实际核实才可判定，随后在总 #17 及 K00/K01/K07/K09 issue 追加执行摘要。

下一批：逐页拆解官方课标包括图形乱码和未编号要求，确认七个真实原子分母；对 8 项范围错配补真正对应的概念/方法/定理和题族，对其余 39 项逐条追补缺项、适用条件和来源校核；继续处理 538 条证明风险与 10 项冲突，教师人工复核以后才能批准和进入教学 Agent。
