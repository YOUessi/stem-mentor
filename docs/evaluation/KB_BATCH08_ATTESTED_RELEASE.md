# Batch08｜独立审校签名与学生端最小提示发布门禁（2026-11-03）

## 本轮新增
已开发仓库外 reviewer 公钥信任配置、离线 RSA-SHA256 验签、完整知识内容 SHA256 绑定、两名独立 reviewer 签名门槛、撤回/篡改/版本漂移失效、student 首层提示最小化输出，以及集合、概率、函数、代数、几何的数学边界回归。

## 明确边界
- 现有 146 篇深度内容仍全部 REVIEW_PENDING，214 条证明步骤并未得到全证明的机器或教师审核。
- 测试使用的两名 reviewer 和 RSA 密钥均为临时虚构身份，只证明软件的签名校验逻辑，绝不代表真实教师批准。
- 尚没有真实教师身份验证、公私钥发放与安全保管、在线审批、未成年人身份/权限或已上线 LLM API Tutor。
- 有合法的可信 reviewer 签名也不意味着可以不核验数学题目的前提、适用条件及学生证明。输出仍标记 CONDITIONS_NOT_ESTABLISHED。

## 仓库外配置和签名契约
真实部署必须先完成独立教研实名与公钥发放；可信公钥注册表 reviewers 包含 reviewer_id、key_id、public_key_pem、active、role=MATH_TEACHER；签名日志 attestations 包含 payload 和 signature_base64。payload 精确包含 knowledge_id、content_sha256、version、reviewer_id、key_id、issued_at、decision。JSON 按 UTF8 sort_keys=True、separators=(",",":") 规范化后以 openssl dgst -sha256 -sign 签署，签名 Base64 保存于仓库外。content_sha256 根据完整 Pydantic lesson model_dump(mode="json") 规范化计算，任何字段改动都会失效。

三个显式环境变量：STEM_MENTOR_TRUSTED_REVIEWERS_PATH（独立信任文件绝对路径）、STEM_MENTOR_REVIEW_ATTESTATIONS_PATH（独立签名日志绝对路径）、STEM_MENTOR_ENABLE_APPROVED_RAG=1。至少两个不同 reviewer_id 的有效且未撤销签名。仓库内签名/公钥配置一律拒绝；无配置、身份失效、签名无效、未来签名、重复或撤回均返回空批准集。生成两对临时测试私钥**不能证明真人教研身份**。

## 对学生只提供最小提示
student_evidence_lookup 仅输出 knowledge_id、curriculum_ids、title、version、hint（第一层）、condition_status、approval_evidence；不泄漏完整证明、解答、反例正文、teacher_solution。现有 editor_draft_search 仍仅用于 Mac 本地编辑，不注册为公用 Web API。已签名知识在新题的可用性仍须额外数学条件核验。

## 独立数学检查与下一步
新增有限集合 16×16 德摩根律、AM-GM 非负条件、等比数列 q=1 分支、乘积求导、多维投影零向量排除、圆弦长退化、方差仿射缩放、贝叶斯分母为零拒绝、容斥和组合边界等精确受控案例。它们是有限子命题和负例，不是整篇证明验证。

后续继续审理 10 项知识冲突、214 条未形式认证的证明步骤，以及选修 A–E 的原子级课标映射；获得真实教研合法审核后才能向学生开放完整知识驱动 Agent。
