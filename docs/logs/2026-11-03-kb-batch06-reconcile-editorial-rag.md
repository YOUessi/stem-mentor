# STEM Mentor｜KB Batch06 安全合并与编辑态证据检索

**日期**：2026-11-03；**执行设备**：授权 MacBook Air（无 Tang / 无外部 VLM API）。
基线：远端 Draft PR #31 `197a0f0756036406cb4ab819a176d0a60ba9548e` 对应的 Mac 等价 Git tree `303319527d2358897349c14a2c90c61c7cef3352`。
新开发位于独立工作树 `~/Documents/文件/stem-mentor-kb-batch06`，不触碰原主仓未提交文件和 Batch02 原始编辑工作树。所有改变经测试后才发布 Draft PR。

## 本次交付

1. 对 Batch02 的 **39 篇已存在但未合并候选知识** 做无损 ID 对照：
   - 29 篇没有同 ID 条目，导入为 `v1/*batch06_import.json`，保留原始学科论证、证明步骤、例题、反例、错因、提示层及 REVIEW_PENDING。
   - 10 篇和既有目录发生 ID 冲突（函数奇偶性/复合函数定义域/分段函数/零点定理/点到直线距离/二项分布/超几何分布/回归统计/三角形面积/向量线性运算）。现行 10 篇不覆盖、不替换；保留原稿和 SHA256、冲突字段到 `KB_BATCH02_RECONCILIATION.json`，状态一律 OPEN。
   - 原 39 篇源稿在 `knowledge/deep/candidates/batch02/` 作为不可由学生 API 自动检索的编辑证据，`scripts/reconcile_kb_batch02.py --check` 保证数据和冲突列表不漂移。
2. 26 张旧方法卡可追溯无损桥：`legacy_method_bridge_v1.json`，原始适用边界、先决结构、提示和许可保存；标记 `NEEDS_DEEP_AUTHORING`，不作为 26 篇新证书使用。
3. 全草案本地 FTS5 检索：`app/deep_retrieval.py`，可按查询/课程 ID/类型获取编辑元数据，禁未认证学生侧访问；教师完整证明只可在受控本地编辑工具显式读取，不注册 HTTP API。学生检索继续返回 NO_APPROVED_EVIDENCE，绝不提前把完整教师解答送往模型。
4. 更新覆盖审计 `KB_COVERAGE_BATCH06.json` 与保守 113 行语义审计 `KB_SEMANTIC_COVERAGE_BATCH06.json`，23 条原有编辑初审语义缺口继续 OPEN（已有草案候选≠正式结案）。
5. 内容总数 **109 → 138**，类型 **58 theorem / 66 concept / 14 method**，独立教师审核 0、学生自有数学推导验证 0，原始 113 工程映射仅“有关联草案”，非官方数学原子全覆盖。

## 严格限制

- 当前 138 篇知识是 **编写并通过数据 Schema 的草案**，不等于 138 个完整数学定理证明，也不等于全部中国高中数学知识。由原定 23 项初审缺口增加候选也没有正式教研复核。
- 本批数学 tests 仅在有明确前提的有限公式/数值样本下作独立旁路检查，不得外推到完整证明、学生得分或现实教学效果。
- 编辑检索里 `scope="EDITOR_LOCAL"` 不是正式鉴权；功能**未注册 Web API**，之后必须独立实现认证的教师审核/许可后才能开放学生证据检索。任何未批准证明与解答都不得出现在 student Agent 的 Prompt 中。
- 现有课标的选修 A–E 以及 113 工程映射的官方细粒度核查仍未完成。所有条目 REVIEW_PENDING。

## Mac 实际验收与日志

- `scripts/reconcile_kb_batch02.py --check`：39 = 29 + 10，0 覆盖冲突；pass。
- `scripts/build_kb_legacy_bridge.py --check`：26 条旧方法卡，无损内容字段检查；pass。
- `scripts/audit_kb_semantic_coverage.py --check`：113 项，23 项 OPEN；pass。
- `scripts/audit_deep_math_evidence.py --check`：48/48 条既有独立子命题；pass。
- `scripts/build_semantic_gap_batch05.py --check`：既有 23 条原始缺口草案冻结来源一致；pass。
- 新增专项测试覆盖 29 导入条目/10 冲突、课程 Schema、编辑态检索和安全拒绝、组合计数/概率/三维向量/直线圆位置等有限旁路数学检查。完整 Python/Node/Chrome 的结果以随本 PR 附带的原始测试日志为准：`docs/logs/kb-batch06/{pytest,new-tests,node,chrome,evaluations}.log`。
- 当前本地 Python **984 passed, 1 warning**；Node **111 passed**。Chrome 全历史绿色 UI、数学实验室、迁移、iPad 触控/压感模拟 **PASS（exit 0，最终 2 passed）**。Mac 浏览器仿真不代表真实 iPad 硬件验证。合成策略 **33/33**、hard-negative 检索 **40/40**、top3 **22/22** 均通过。
- `git diff --check`、独立 Git tree 以及远端 PR/CI 须再次核对，不允许发布未通过完整回归的版本。

## 下一批

完成 10 个编辑冲突的逐项数学依据与来源复核、独立确定是否合并/废弃；对新增 29 篇逐一定理建立假设→证明义务→反例的更强数学验证，不靠有限样本推断全量证明；以正式可核对的课标分母建立 A–E 选修真实原子映射；同时构建有独立教师审核后才能进入学生 Agent 的知识发布管道。
