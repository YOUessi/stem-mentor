# STEM Mentor｜Batch141 Mac真实开发、数学审查及测试交付报告

本批源于GitHub远端 81cf8958ab41b31ddf747fbe4c7a5de52d1a57e6；已同步源提交 81709068e0f2768791d51bdc7d738fd161bb7c76。最终证据提交SHA以Draft PR远端为准。
所有源码、审查材料与测试均在授权MacBook Air生成；Tang未使用，Mac主仓未提交修改保持不动。

## 实际成果与严格数学边界

- K01/K07：对剩余47个历史P0步骤，把KB29/30已有的数学前提、反例和历史步骤claim/reason逐项SHA-256双重锁定，统一可审查格式。新格式来源卡从80/127到127/127。
- **这47条并不是47条从零推导的完整证明**；KB28/29/30此前已覆盖127/127历史编辑审核草案，迁移仅提升来源完整性、卡片一致性及变更门禁。
- K07：独立SymPy和精确有理数检查12条高风险步骤的12个合法及12个失效输入，共24个有限实例。其他35条本批未增加独立数学Oracle，不夸大验证。
- K09：每张来源卡对历史条件、失效边界、原步骤SHA和旧档案SHA执行回归，并注入伪批准、伪造分母、偷换前提等负例。
- K08：学生端检索继续NO_APPROVED_EVIDENCE，不展示TEACHER_ONLY完整解答。所有教师稿状态REVIEW_PENDING。
- 当前538个旧证明步骤仍未形式认证；10项数学冲突未裁决。七轨正式课标分母UNKNOWN；教师审批0、权威发布0。
- 本批不新增正式深度讲义；此前57份仍为有界教师候审稿，不是正式课程覆盖率。

## Mac真实测试

| 测试 | 结果 |
|---|---|
| Batch141独立专项 | 934 passed（同全量运行重复，不累计） |
| Python完整后端 | 66,293 passed · 5 skipped |
| Node | 111 passed |
| 受控Chrome/Playwright | EXIT 0；浏览器pytest 2 passed（不等于真实iPad） |
| Mac原始PDFKit授权课标指纹 | PASS：本地重放，CI只核提交摘要 |
| Batch141独立数学Oracle | 24/24个有限精确实例；非一般证明 |

## 原始日志/退出码SHA-256（可重复哈希验证）

| 日志 | Exit | SHA-256 | 字节 |
|---|---:|---|---:|
| docs/evaluation/logs/KB_BATCH141_FOCUSED.log | 0 | 04a17a420f3fe4dd0e9cc1c246bcadaa41fd09a9bacb8fdc530308b8283425fd | 1061 |
| docs/evaluation/logs/KB_BATCH141_MAC_FULL.log | 0 | 7fe353af38362957f642f60615cbed97a9e57df910030f7ccef4f38e37117677 | 134114 |
| docs/evaluation/logs/KB_BATCH141_BROWSER.log | 0 | b88533d9affa2c9f24009ef72606317225d81257ef9fec83e01ddaa16af0170a | 2442 |

日志由Mac实际运行生成，GitHub CI复核日志字节及条件文本，不得声称CI能重做私有PDF重放。

## 发现、失败与下一批

- Mac GitHub HTTPS fetch由于低速超时（低于100B/s超过15秒），源码通过GitHub原生Git对象API非强制快进提交；远端Git Blob需逐文件验证SHA。
- K00：按正式课标编号要求逐条拆分、去重与七轨课程分母冻结，仍需原文证据及真实教师裁决。
- K07：优先对47条中本批无独立数学Oracle的35条补量词证明级审核，并继续逐项处理538历史未认证步骤、10个冲突；不可把127张卡等同于证明认证。
- K02–K06：恢复必修到选修的整模块原创深度讲义、题族、错因、提示与近远迁移，继续在K08/K09接入独立教学Agent评价。
- 所有材料继续只供教师候审，学生未获批准的权威检索和自由文本步骤认证保持拒绝。
