# STEM Mentor｜Batch115 原创数学知识、课标证据与重启可复现验收

## 事实源及边界

- 代码事实源：GitHub `YOUessi/stem-mentor`，总任务 #17，子任务 #18–#27；[Draft PR #140](https://github.com/YOUessi/stem-mentor/pull/140)，基于 Draft PR #139 的 Batch114 分支，保持 Draft，不合并 main。
- 唯一开发、知识生产与测试环境：MacBook Air；独立工作树 `~/Documents/文件/stem-mentor-kb-batch115`，分支 `feat/kb-batch115-official-source-risk`。未在 Tang 上开发或测试。Mac 主仓有独立未提交工作，未触碰。
- 本批数学内容首次源代码本地提交：`10cac74df09cffc3e0385fafe060a7f399fafadd`。GitHub 原生远端提交 SHA 与本地可能不同，必须以 PR HEAD 实测校验；13个首次源文件 Blob SHA 已逐项验证相同。
- 来源：《普通高中数学课程标准（2017年版2020年修订）》合法公开 PDF；已核对文件 SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。**不提交 PDF、原文抽取段落、学生信息**；仅源位置/指纹与原创编辑释义进入 Git。

## K00 / K01：真实范围审计与 Schema 门禁

- 印刷页 **25、26、62、63**：PDFKit 原始行数 `25+29+25+23=102`，全部源行由本机原始 PDF SHA 锁定；4页均具有完整连续结构分区，本批共 **24条编辑性要求候选**，必修13、选修B11。8项有有限精确见证；其余概览/教学要求不可假装为数学定理。
- 课标结构来源登记 **18/61页**，其余43页尚需同等结构审查；**教师核对并正式完整原子化0/61页**。七轨正式课程原子分母全部 `null` / UNKNOWN；不能用候选数、113条工程目录或490份草案制造虚假完成率。
- 条件校验拒绝跨轨错误、无出处、重复结构、伪造教师批准/形式化认证及来源漂移；冻结 Batch114 历史深度讲义统计，后续Batch115增长不能追改旧审计分母。

## K02–K06：8份原创候审深度讲义

依次覆盖：(1)平面自由向量、零向量与相等；(2)向量加减和长度；(3)数量积、夹角的非零前提；(4)非零向量垂直当且仅当点积为零；(5)伯努利独立样本的MLE和端点；(6)单侧显著性检验p值与后验概率之别；(7)带截距最小二乘斜率及 `Sxx>0`；(8)离散指数模型的相对增长与外推边界。分类3定理、2概念、3方法。

共 **16道教师完整例题、24级启发提示、16项近远迁移、8组反例、9条新增未认证证明步骤**。每份记载正式定义/完整假设/适用域、论据步骤或方法合法性、典型错法及独立有限示例检查。示例：零向量与非零向量点积为零不能宣称存在90°夹角；伯努利参数开区间全成功样本不具有被取到的MLE；`Sxx=0` 时斜率 `0/0` 不合法。所有内容仍为 `REVIEW_PENDING/TEACHER_ONLY`，不得作为学生端权威检索或泄漏独立挑战的教师答案。

## K07–K09：实际测试、失败与 Mac 原件缓存修复

- 本批独立有限精确或 SymPy 数学示例、假设失效负例、Schema/来源/索引安全专项：**237 passed / 0 failed**（首次专项两项历史快照计数漂移失败，已冻结历史分母并重跑通过）。
- Mac Chrome/Playwright 浏览器回归通过：模拟移动端、虚拟 iPad 触控及笔压，**浏览器pytest 2 passed**；这不等于真实 Apple Pencil 硬件验收。
- **真实环境失败1**：首次完整 Mac 测试超过90%后设备突然重启，自动执行流程被中断；原始日志 `KB_BATCH115_MAC_CHECK_REBOOT_INTERRUPTED.log`，不得称通过。
- **真实环境失败2**：设备重启清空 `/private/tmp`，旧构建链所需的 `kb56_page_15.txt` 等 PDFKit 页面缓存消失，第一次重新执行在 Batch64 本地来源验证阶段报 `FileNotFoundError`。日志 `KB_BATCH115_MAC_CHECK_MISSING_SOURCE_AFTER_REBOOT.log`，不得称通过。
- **本轮工程修复**：在 **Mac** 重新下载公开课程标准并核对整PDF精确SHA；新增 `scripts/kb_mac_restore_pdfkit_source.swift`，从合法原件以系统 PDFKit 恢复 **61/61** 个纸质页13–73对应的页面缓存。恢复前先逐页验证与仓库锁定的61个SHA256全部一致，才写入仅 Mac 私有临时目录；程序不输出课标原文，也不提交源 PDF。
- `scripts/mac_check.sh` 新增缺页前置检测，重启后只在 Mac 本地已提供SHA匹配源PDF时自动恢复；缺乏合法原件则**明确退出12**，不能悄悄用假内容通过测试。Mac 私有持久源路径 `~/Library/Application Support/STEMMentor/sources/official_math_2020.pdf`，未入库。已经实际执行全量61页恢复成功、错PDF拒绝检查及Batch64旧门禁验证通过。
- 完整Python/Node/策略/检索与浏览器的最终退出码：**Python 65,918 passed / 5 skipped / 1 third-party warning; Node 111/111; policy/retrieval, JavaScript syntax, and offline simulation sections all reached their successful terminal markers (full wrapper was not captured with a separate exit-code file; do not infer a formally observed numeric exit code)**。所有最终原始日志 SHA256 见下表（稍后由脚本按真实文件计算）。

| Mac evidence log | SHA-256 |
|---|---|
| `KB_BATCH115_BROWSER_FINAL.log` | `5bc0a5caf9dc3092cedda857a1d8e6e8a07de054b84b5740d8217c0e6c3444be` |
| `KB_BATCH115_FOCUSED_FINAL.log` | `4d94c8694e1c2711d8417e6aa16f5df8e2c31501ab2738e064151f5dd362d3a6` |
| `KB_BATCH115_FOCUSED_INITIAL.log` | `f4283cb57156c016ea01214ec3bbfb42fd0c9742ae0bc6b8c334c17c8ebdc7e1` |
| `KB_BATCH115_MAC_CHECK_FINAL.log` | `ce8043a632f9e90fcaf93f9853b91f94caf70142042988674d0f35b18c13981f` |
| `KB_BATCH115_MAC_CHECK_MISSING_SOURCE_AFTER_REBOOT.log` | `1f5149593fa0b95c0ef53c639c636d1d8934399c691818545dbac256b313a1ce` |
| `KB_BATCH115_MAC_CHECK_MISSING_VISUAL_AFTER_REBOOT.log` | `7cde6ae4c0ed2869fb21f1ce66b1c4b34213cb81e6dabcd750d99075bc7b379f` |
| `KB_BATCH115_MAC_CHECK_REBOOT_INTERRUPTED.log` | `e6be4b9d9b7e1c790306d1684a8956cb67840a1f5d66056e7b99fa99e77ba9c5` |
| `KB_BATCH115_SOURCE_BUILD_INITIAL.log` | `cdbfd306beabb16f9890b7059a1fb6960dff98e38e161493222b116db2ea235f` |
| `KB_BATCH115_SOURCE_CHECK_FINAL.log` | `cdbfd306beabb16f9890b7059a1fb6960dff98e38e161493222b116db2ea235f` |

数学有限实例校验不等于完整普遍性定理的形式证明，更不等于教师审核、学习增益验证；学生自由文本未验证步骤始终未认证。

## 未完成与后续批次

- 七轨正式官方知识原子分母仍 **UNKNOWN**，教师完整逐页原子化0/61；历史未审核先修关联**172条**、历史未认证证明步骤**538条**、10项数学冲突未裁决。新增9条候审证明也未认证；教师正式批准和学生权威发布仍为0。
- 下一批：使用已验证原始 PDF 在 Mac 上批量核对余下43页的**章节/轨道/课程要求**，从逐页结构登记转向完整章节可审校原子台账；同时集中处理函数复合定义域、概率条件独立与向量零/退化的历史冲突及先修语义关系。将可机器检查的实例、失效反例与人审签署分层记录；逐章推进到学生端有真实审核的RAG层。
- 所有长期任务继续保持 Draft、REVIEW_PENDING，绝不将源码通过或课程候选计数等同于正式完成。
