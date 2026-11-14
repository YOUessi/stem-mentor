# KB157｜授权Mac原创高中数学知识库开发及完整真实验收（2026-11-14）

源代码 SHA: ab3b93e4bd8ba91d7779715efb3927bc019dcdcb。独立Mac feature worktree，不改脏main、不使用Tang、不强推或合并主分支。
新增十篇原创教师候审讲义：必修集合列举与描述、指数时间尺度、经验概率；选择性必修抛物线/双曲线参数退化、正态标准化；选修A自然常数e有限序列/B闭区间极值/C演绎归纳/D周期模型/E复利选修案例。
每篇均含正式定义或定理、全部假设、4条分步论证、适用边界和反例、典型错解及修复、2道原创教师例题、3级无剧透提示及近远迁移。新增20题、30级提示、20项迁移。
新增K00七轨315条逐来源行哈希可审计标记审查义务、32项CDE非编号提案与89条历史边界关系。原始PDF仅在授权Mac上PDFKit复核；315绝不是官方知识原子分母，所有七轨官方分母UNKNOWN。
239条历史编辑候选中124条已关联候审稿，115条未关联；全部165份仍REVIEW_PENDING/TEACHER_ONLY，教师批准0、学生权威发布0。
新增40/40独立SymPy精确有限校验，20项有效/边界、20项失效前提/错误泛化拒绝；不构成一般形式证明、真人审核或学生自由解题认证。
编辑端本地FTS检索和仅聚合状态API，学生请求保持NO_APPROVED_EVIDENCE，教师完整解答不进入学生查询索引。

## 实际Mac测试（包含交叉重复，不能简单相加）

| 项目 | 结果 |
|---|---|
| Python后端全量 | 66,293 passed, 5 skipped |
| Node | 111 passed, 0 failed |
| Batch157专项回归 | 647 passed，1条第三方弃用警告 |
| 初始专项失败保留 | 313 passed，334 errors（同一K00表格输出顺序根因），退出码1；修复后647通过 |
| 独立有限数学核验 | 40/40，20项失效前提 |
| Chrome模拟 / 浏览器pytest | 9 checks / 2 passed（非实体iPad） |
| 完整Mac验收 | EXIT 0 |

## GitHub源码CI失败与修复（非Mac测试）

首次源代码提交的GitHub Actions #43592314363 FAILED：646项通过、1项失败。失败项是直接在Linux runner读取Mac私有 `/private/tmp/kb117_pdfkit_lines_private.json`，与数学断言失败不同。
修复：Linux runner仅对仓库中已锁定的十组PDF行哈希、页码/行范围及作者候审数据执行一致性门禁；Mac保留且强制实际原始PDFKit行重放，绝不将私有PDF或课标全文上传CI。修改后Mac专项647/647通过。远端新Commit CI终态需再次独立核验。
证据归档验收补充：首次联合运行662项通过、14项共因setup错误，原因为报告按dict插入顺序列出5套日志，而JSON manifest使用sort_keys；修复后使用固定顺序，加入JSON roundtrip负面回归。再次Mac联合运行676项通过，新加入的独立顺序回归随后复跑，不把这些重叠测试算作新讲义。

## 实际Mac stdout与exit原始哈希

| 日志类型 | 退出码 | stdout字节数 | stdout SHA256 | exit SHA256 |
|---|---:|---:|---|---|
| FOCUSED_INITIAL | 1 | 364357 | 0cd3379a54796e84c8eb555c64a924e2982465eb3acaca4b5762d1a7715b3c86 | 4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865 |
| FOCUSED | 0 | 1271 | b90ce864d2a484a1a5051a52873d23b7adc9c499d82d24094ebb1819153c578b | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |
| NODE | 0 | 20914 | be3569d9ae59009808b7de7941993779b6fc8186b77240eeae0342313453828e | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |
| BROWSER | 0 | 2443 | bdcf4d6af36a02c203eddf1762e4f80c530f08429459bd26d380622019e7dec0 | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |
| MAC_FULL | 0 | 154849 | 2c341e8cabbeb037b93471028a9b49f2e52223564a6c57ecf6a7f04bf4d357c5 | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |

版本化Manifest与五套stdout/exit逐字节锁定；CI是远端独立运行，不把Linux CI冒充Mac。
## 下批

K00继续官方课程要求逐句拆分、跨页语义去重和人工审校，冻结七轨实际原子分母；K02–K06按115条剩余历史候选继续整模块扩展。
K07历史538条一般形式未认证证明步骤和10项数学冲突仍需实质评审；K08未见题的规则baseline和真实API还缺独立对照，教师审核为正式发布必要条件。
