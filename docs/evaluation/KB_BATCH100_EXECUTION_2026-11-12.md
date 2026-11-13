# STEM Mentor｜Batch100 Mac-only 交付与验收证据（2026-11-12）

## 源码及隔离边界
- 上游 GitHub Draft PR #124: `feat/kb-batch99-editorial-math-validity`，远端 HEAD `52001f710c18d05ad0a9df10553836dab37b567b`；其 Actions #43076146047 结论 success，test job **171/171** 成功步骤。
- Mac 原工作树：`~/Documents/文件/stem-mentor-kb-batch100`，已保存基线提交 `6394ca484f048fa69d2ed1aaaeb27cc327389f98`。不触碰主仓 main、Tang 或其他项目。
- 本次 GitHub 祖先兼容的独立交付工作树：`~/Documents/文件/stem-mentor-kb-batch100-delivery`，分支 `feat/kb-batch100-verified-delivery`。从真实远端 `52001f7` 创建，干净地 cherry-pick 20份讲义提交；原先基线树 `805222b1afdd535a6a70c496728f541a76254a77` 不变。
- Batch100 完成数学负例修复后的源码提交 `5740267dab63f144ee2de7d53235734622653780`；对应源码 Git tree `b63288f4548cc6f9c45ce93df5afb310449b62f8`（不含本报告与日志）。
- 数学审查追补源代码修复：Mac 本地提交 `50cbe80d64102eee4f058884994966be9889c75e`；源码 Git tree `c55c6a6d22e73c3f888bc64b98d85d4547d8b7f0`。Mac HTTPS push 因限速超时失败，GitHub 原生连接器仅负责同步，五个 Blob SHA + 整个 Git tree 与 Mac 一致；GitHub 远端对应提交 `8ffdeab5a2d4104dddd5046eb73a661f73741ef3`，PR #125，未覆盖未提交文件、未强制推送。

## 交付内容
- K02–K05/K06：从已有项目临时来源候选中挑选 **20项**，编写原创中文结构化深度数学草案，配套40份教师例题、60条三级提示，以及解释、前提、符号、三步证明（适用于定理）、反例、错因与近远迁移；全部 `REVIEW_PENDING / TEACHER_ONLY`。
- K00：20条来源锚点保留 source page、原行 SHA256、快照 SHA256 与未审校的工程映射候选；300条临时标签不作为官方课程知识原子。项目累计深度草案 **86** 份。
- K07：20个精确有界实例检查器和输入失败检查，不宣称形式化普遍证明。额外修复3D直线-平面判定中 `zip` 对维度不一致的静默截断、最小二乘在空设计矩阵或多目标输入时的不合法接受，增加7项直接负面回归。
- K07 数学审查追加：`math.hs.batch100.11` 曾不恰当地声称「非凸多边形等于其顶点凸包」。现明确区分凸多边形的顶点凸包等式与简单非凸多边形的三角剖分论证；新增 `backend/tests/test_kb_batch100_nonconvex_proof.py` 使用凹五边形面积 `3`、其顶点凸包面积 `4` 的构造性反例，并检查作者源→结构化课程证明条目的修复。此反例属于一般陈述的边界检查，不是自动教师认证。
- K08/K09：学生端仅 `NO_APPROVED_EVIDENCE`，不返回教师完整解答；历史132加本批40段文字先修，共 **172条未绑定为已审校知识 ID**，**0条**被未经核对地提升为正式先修边。
- 工程来源轨道对本批20条：16条 `MATCH_EDITORIAL_ONLY`，4条 `TRACK_UNRESOLVED`；所有匹配仍为未进行语义教师核对的编辑候选。

## K00 七轨*临时工程来源*矩阵（不是课标原子分母）
| 编辑轨道 | 临时来源标签 | 教师待审深度草案 | 正式原子分母 |
|---|---:|---:|---|
| 必修 | 75 | 4 | UNKNOWN |
| 选择性必修 | 66 | 27 | UNKNOWN |
| 选修 A | 60 | 18 | UNKNOWN |
| 选修 B | 60 | 21 | UNKNOWN |
| 选修 C | 31 | 11 | UNKNOWN |
| 选修 D | 8 | 5 | UNKNOWN |
| 选修 E | 0 | 0 | UNKNOWN |
| 合计 | 300 | 86 | UNKNOWN |

## Mac 测试原始证据
测试环境：MacBook Air / macOS 26.3.2 / Python 3.13.13 / pytest 8.4.2 / SymPy 1.14.0 / Node.js v22.23.1。执行 `bash scripts/mac_check.sh`，独立 Chrome/Playwright 脚本另行实跑；不使用 Tang 或未经授权的模型API。

- 第一轮全链路测试（补强维度门禁之前）：`docs/evaluation/logs/KB_BATCH100_MAC_CHECK.log`，Python **63,374 passed / 5 skipped / 1 warning**；Node **111/111 passed**。该日志不能替代最终补强后版本的回归。
- 修复后原工作树专项：`docs/evaluation/logs/KB_BATCH100_FOCUSED_FINAL.log`，**115 passed**，退出码 0。
- 补强后交付树 `5740267` 的专项测试：`docs/evaluation/logs/KB_BATCH100_DELIVERY_FOCUSED_FINAL.log`，**115 passed / 0 failed / exit 0**（80.99 秒），其中新引入的7项恶意维度/输入形状用例单独复测 **7 passed / 108 deselected / exit 0**。
- 补强后、非凸证明修正前的 Mac 全量重跑：`docs/evaluation/logs/KB_BATCH100_MAC_CHECK_PRE_NONCONVEX_FIX.log`，**63,381 passed / 5 skipped / 1 warning / exit 0**。该日志不覆盖最终证明条目。
- 非凸证明修正后的单元+批次专项：`docs/evaluation/logs/KB_BATCH100_PROOF_FOCUSED_FINAL.log`，**116 passed / exit 0**；含凹五边形构造性反例。
- 最终证明修正后的 Mac 全量测试：`docs/evaluation/logs/KB_BATCH100_MAC_CHECK_FINAL.log`，**63,382 Python passed / 5 skipped / 1 warning；Node 111/111 passed；`BATCH100_AFTER_PROOF_MAC_CHECK_EXIT=0`**。这是提交证明修正后同一源码的最终 Mac 全量结果。。
- Chrome/Playwright 真浏览器全套：`docs/evaluation/logs/KB_BATCH100_BROWSER_CHECK.log`；16个测试脚本/pytest调用（15个浏览器脚本 + 1个含2个pytest用例的调用），全部通过，**浏览器 pytest 2 passed；最终 exit 0**。临时数据库清理，无真实学生数据。包含多个屏宽、几何交互、触摸笔模拟及负面输入；不把模拟触控声明为物理设备测试。
- 以上专项测试均是全量 Python 子集，不与全量通过数相加。CI、有限代数示例与教师正式审核是三个不同维度。
- GitHub 最终证据提交后仍需独立查看 GitHub Actions，不能仅因 Mac exit0 宣称 CI 成功；本地所有日志均为原始测试记录，不等价教师审核。

## 禁止误报的剩余缺口
- 134条临时主题尚未成对语义比较；正式七轨课标原子分母仍未知，教师逐页原子化 **0/61**。选修 E 的零条工程来源标签不是官方“选修 E 没内容”的证明。
- 历史待验证证明步骤 538、P0 无直接教师卡 106、数学冲突 10，未凭有限算例提升为已认证。
- 教师批准 **0**；学生权威发布 **0**。全库及本批均不允许模型 API、CI 或结构完整度自动审核升权。

## 下一批的可验收开发链
1. K00 将61页课程依据逐页转为带来源页/段/轨道/冲突说明的正式原子候选，分别生成必修、选择性必修和选修 A–E 的**有分母证据**覆盖矩阵；继续裁决134条未成对比较主题，不得把临时标签数当官方分母。
2. K01/K08 将172段文本先修逐一候选映射并处理跨轨、同名、多义、循环及人工审核状态；不把自动匹配结果发布到学生先修图。
3. K02–K06 从覆盖缺口继续成组开发原创讲义及题族；K07逐步检查538条待认证证明步骤与10个冲突；K09以真实教师签名为批准前提，增加未见题、安全检索与浏览器回归。
