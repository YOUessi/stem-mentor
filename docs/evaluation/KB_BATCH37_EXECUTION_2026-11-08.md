# STEM Mentor｜Batch37 数学范围错配修复与审查门禁（2026-11-08）

## 实际任务边界和 Mac 环境

开始前使用已连接的 GitHub 接口读取总任务 #17、十个子任务 #18–#27、最新 Draft PR #61、源码与版本化 Batch36 审计。所有 11 个任务保持 OPEN。Batch36 的冻结 47 条关联风险为 12 条 CLAUSE_UNVERIFIED、27 条 PARTIAL_SCOPE、8 条 CLAIM_MISMATCH。

本批 **唯一开发和测试设备为用户授权 MacBook Air**。从本机 Batch36 已提交源码树建立独立 worktree：
- 主仓：/Users/youtang/Documents/文件/stem-mentor，main 原有 11 处未提交项保持原状；
- 独立工作树：/Users/youtang/Documents/文件/stem-mentor-kb-batch37；
- 功能分支：feat/kb-batch37-scope-repair；未合并、重写或强推 main；
- Tang **没有使用**。浏览器及数学测试使用合成数据，没有上传真实学生数据。
- 先前 Batch36 在 Mac 与 GitHub 的 commit SHA 不同，但基线文件 Git Tree 一致（2c1bbf16ac8febc5e2104d312ad886a8ef188c92）。Mac Git fetch 本次 SSL timeout；故按已核实远端基线使用 GitHub 原生 Git object 接口，无强推同步，并对每个 Git blob 校验与 Mac SHA 相同。

## K00 / K01 / K05 / K06：八项明确数学范围错配，逐项新增完整原创教师审核稿

使用 Batch36 冻结的 CLAIM_MISMATCH 列表 **8/8 项**，一对一建立：
- 选修 A：数列极限四则法则、三维向量投影与夹角、三维正交等距变换；
- 选修 B：空间两直线距离的非平行/平行分支；
- 选修 C：加权算术/调和均值与测量尺度、恒定相对增长指数模型与真实人口外推；
- 选修 D：严格黄金分割代数比值与审美越界；
- 选修 E：理想球面大圆短弧、欧氏弦长、对跖退化。

一共 **8 篇原创结构化教师侧审核稿、16 道有明确步骤和答案的教师侧例题、8 个具体反例、24 级循序提示、8 组近迁移和远迁移对**。各项有真实数学前提、3–4 条分步推导及合法依据、具体反例、方法失效边界、典型错法。完整正文在 KB_BATCH37_EIGHT_SCOPE_REPAIR_MANUSCRIPTS.md（468 行）；结构化来源在 knowledge/editorial_review/kb_batch37_scope_repairs.jsonl，完全由 scripts/author_kb_batch37_scope.py 可复现。

与历史错配的旧讲义不等价的事实继续保留；新稿只作为额外对口内容，不能把原来 47 项关联改成课标认证。使用 Pydantic 严格 Manuscript37 类型、冻结源 SHA、目标集合、内容哈希及教师非公开投影，拒绝重复、伪造教师批准、正式发布、错误来源绑定。

## K07 / K09：独立有限数学验算和负例回归

新增 8 类明确限定域的精确验证算子（Fraction 与整数）：极限商实例、三维向量投影、三维正交对角变换、两空间直线距离平方分支、正权重平均与调和平均、固定增长率离散递推、黄金比例有限整数残差、理想球面三种特殊中心角。

针对每类提供 **1 个合法输入和 1 个非法前提输入**，并额外测试空字段、附加字段、布尔/浮点/字符串冒充、超大整数、未知算子及几何退化。所有通过的输出仅为 FINITE_EXACT_CASE_ONLY；不支持未知数学结构返回 UNSUPPORTED，前提不足返回 CONDITIONS_NOT_ESTABLISHED。没有把有限样本算术运算误标为证明、教师批准或学生自由步骤 VERIFIED。

回归文件 backend/tests/test_kb_batch37_scope_repairs.py **60 项通过**，包括具体一对一课程候选匹配、冻结稿件哈希、独立反例绑定、非公开可见性、伪造批准否定测试和参数边界负例。Mac CI 脚本与 GitHub Actions 均新增生成器 --check 门禁。

## 真实 Mac 测试与失败修复

- 源内容生成复验：三份生成输出均与作者源代码完全一致。
- 新增 Batch37 pytest：**60 passed / 0 failed**（完成源文稿换行修复后重新执行）。
- Mac 全量 Python：**37,732 passed / 0 failed / 1 项第三方弃用 warning**，耗时 **144.25 秒**。
- Node 测试：**111 passed / 0 failed**；教学策略冻结评测通过 33 项，困难负例检索 40 项及 Top3 22 项，均无失败（详见 mac_full_check.log）。
- Chrome/Playwright 浏览器 15 项脚本均通过，另有浏览器 pytest **2 passed**；总出口 BROWSER_BATCH37_EXIT=0。使用临时合成数据库，iPad 是指针/压力模拟而非实机。
- Mac 总检查出口 **MAC_BATCH37_EXIT=0**。
- 真实发现并修复：第一次尝试源码提交时 git diff --cached --check 检测到 Markdown 最后多余空行；修改源生成器统一单个 EOF 换行，重新生成文稿并专项复测通过。没有删除检测步骤以掩盖问题。
- Mac 运行回归时，历史 evaluations/results/2026-10-15-policy-and-retrieval.json 和 evaluations/results/2026-10-15-v05-retrieval.json 仅刷新运行时间戳，提交前在隔离 worktree 中恢复，保持原冻结对照样本不变。
- 本批不运行专用 GPU 推理；模型 API、任何数学一般定理的完整形式认证、真实教师授课有效性评测均不在本轮测试范围。

版本化原始日志：
- evaluations/results/2026-11-08-kb-batch37/mac_full_check.log
- evaluations/results/2026-11-08-kb-batch37/browser.log

## GitHub SHA 与完成边界

Mac 源码提交：f7d22cfbf6605332d2e68d9944cdc405fd876507；源码 Git Tree：70b956174eeaffd475fc2937d5c1704f487f6ad8。
GitHub 原生提交：22909ea11642d91208d50bedc55188987d576dc4；已逐项核实 9 个 Git blob SHA，**同一 Git Tree**：70b956174eeaffd475fc2937d5c1704f487f6ad8。
远端 Draft PR：#62，基于 #61 的 GitHub Batch36 HEAD，不触碰主分支。最终报告和测试日志另行提交后，以 GitHub 实际 HEAD 和 Actions 状态为准，不提前宣称成功。

**不可虚报的范围**：既有深度知识 JSON 草案仍 **287 篇**；独立教师审核稿从 49 篇增至 57 篇，其中本批 8 篇，全部 NOT_FORMALLY_CERTIFIED / REVIEW_PENDING / TEACHER_ONLY，未写入学生权威检索索引；正式教师 APPROVED=0，学生深度内容发布=0。现有 313 项项目自编编辑目标不是官方课程原子分母，必修、选择性必修与选修 A–E 共七个官方原子分母继续为 null。历史 538 个未形式认证步骤和 10 组未裁决冲突未冒充已解决。

## 下一批依赖和执行建议

1. **K00**：回到官方 PDF 逐句核对印刷 52–73 页中选修 A–E 相关条款，尤其缺失/乱码/未编号要求，形成七轨道可复现完整原子分母与内容缺口，不用页级项目原创候选代替正式覆盖。
2. **K01/K05/K06**：逐项补充剩余 39 条非认证旧关联的确切数学技能缺口与必要反例，对本次 8 份新稿开展独立教师审阅；批准前保持学生侧不发布。
3. **K07**：优先处理 538 条尚未认证的证明步骤与 10 组历史冲突的真正数学核查、证明域条件和反例，不把数值测试误认为符号全称证明。
4. **K08/K09**：补齐真实 Agent 使用的严格审批索引、不同提示预算和真实 API 的对照冻结评测，绝不泄漏 teacher_solution。完成每章教师批准及发布审核后才可计入学生正式覆盖。
