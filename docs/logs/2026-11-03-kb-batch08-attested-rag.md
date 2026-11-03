# STEM Mentor｜Batch08 受审核知识发布门禁与独立数学边界验证

日期：2026-11-03，MacBook Air 独立 worktree。
基线：feat/kb-batch07-syllabus-proof-audit，commit a3861abdf76165e98a05a5309cc0e90147296339。该分支叠加此前知识建设 Draft PR；main 仍未合并这些草案。

## 一、本轮真实改动
1. backend/app/attested_releases.py：新增仓库外可信 reviewer RSA-SHA256 验签、带签名的教研审批、整个知识文档的规范 JSON SHA256 锁定、至少两位不同 reviewer 签名、撤销和各种畸形配置 fail-closed。不会让源代码中伪造的 APPROVED 状态转正。
2. backend/app/deep_retrieval.py：为 student_evidence_lookup 接入批准列表，遵守仅第一层提示、不给完整 teacher_solution 和证明，条件始终为 CONDITIONS_NOT_ESTABLISHED；在 SQL 全量匹配后按 approved_ids 限制，避免前 20 条截断导致已审证据误漏。
3. backend/tests/test_attested_release_batch08.py：临时双 RSA 测试公私钥的离线试验签名、版本哈希篡改、签名篡改、伪造身份、重复/撤销、未来时间、被停用 reviewer、仓库内信任文件拒绝、学生防泄露回归。测试身份全部为临时合成，不能当真实老师。
4. backend/tests/test_batch08_math_conditions.py：集合德摩根律 16×16 全枚举、AM-GM 非负域、等比求和边界、导数乘积、向量投影非零约束、弦长退化、方差、Bayes 条件概率、容斥和组合数等 11 组分类型严格实例核验。它们**不是 66 个定理共 214 条证明步骤的正式认证**。
5. scripts/audit_kb_attested_release.py、GitHub CI 与 docs/evaluation/KB_BATCH08_ATTESTED_RELEASE.md：检查发行默认 fail-closed，防止 CI 被注入外部 reviewer 密钥；文档明确真实教研身份尚未实现。

## 二、Mac 真实验收（完整日志）
- Python 全量 1649 passed，1 个已有 Starlette/anyio 弃用警告；新增专项 334 passed。测试命令：PYTHONPATH=backend .venv/bin/python -m pytest -q backend/tests。
- Node.js 111 passed（node --test tests/node/*.test.cjs）。
- 教学策略 33/33、hard-negative retrieval 40/40、top3 22/22。
- 既有 Batch07 数学证明义务和课程语义审计 --check 均通过。
- 完整 Chrome 回归 PASS：绿色 UI、v0.7–v0.12 动态实验室、迁移、iPad 手写/双指缩放/模拟压感及 2 项浏览器 pytest 全部通过。仅浏览器/笔模拟，不是真实 Apple Pencil 硬件验证。
- CI 新增无审批默认门禁检查。实际远端 CI 状态要在创建 PR 后再单独核对。
- 机器审计：deep_draft_count=146，REVIEW_PENDING=146，真实批准=0，正式 student evidence released=0。

## 三、缺口与下一批
- 10 项 Batch02 版本冲突仍在 HOLD，不得自动选择；214 项理论证明步骤仍没有正式完整验证。
- 18 个 A–E 高层主题仅是工程槽位，官方细颗粒课程原子映射 0。
- 真实教师实名审查、公钥申请与独立私钥托管、授权教师签署界面、审批结果的外部权限隔离/审计、正式云端 VLM/LLM Provider 和学生题目步骤检验未完成；本批只交付了可回归、默认为关闭状态的**签名发布基础设施**。
- 下一轮应优先验证真实课程原子范围并扩大有证明/反例的高质量知识、独立审理冲突、构建真正教师审核和安全 API Tutor 端到端测试。不能以机器签名代替真人教师教学质量判断。

## 四、回归原始证据
参见 evaluations/results/2026-11-03-kb-batch08/ 里的 python.log、node.log、browser.log、attestation_audit.json、tutor_policy.log、retrieval.log、proof_audit.log 和 coverage.log。
