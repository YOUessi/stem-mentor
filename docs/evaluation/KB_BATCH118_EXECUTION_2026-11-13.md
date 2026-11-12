# STEM Mentor / Batch118：课程来源枚举线索、概率统计讲义、审核隔离与机器验证

## 事实源与执行边界

- 源码开发和验证设备：授权 **MacBook Air**，新建独立 worktree `~/Documents/文件/stem-mentor-kb-batch118`，分支 `feat/kb-batch118-source-denominator-probability`。父提交 Batch117 `dfd7ca6959edda83f0e57e109da2b09bc0c18422`。原本 main 和 Batch117 的未提交评测快照均未覆盖。
- 标准版本：《普通高中数学课程标准（2017年版2020年修订）》，来自本机合法来源原件，PDF SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`，含188个物理PDF页；本次编制范围为旧课程章节印刷13–73页（61页）。绝不在GitHub上传课标正文、原始PDF、学生真实数据。
- 11个Issue（主任务 #17，子任务 #18–#27）启动前从GitHub实际读取，均Open。原 Batch117 Draft PR #142仍Open / Draft，基线 HEAD 已核验；未合并 main，未强推。
- 所有新知识为 **PROJECT_AUTHORED + REVIEW_PENDING + TEACHER_ONLY**；一般定理的外部教师认证仍为0，学生自由文本步骤仍不得因LLM自信而自动验证。

## K00 / K01：机器可审计来源候选，但**不伪造官方原子总分母**

新增可重建 `scripts/build_kb_batch118_source_atom_ledger.py`，核对Mac PDFKit缓存的每一来源页与Batch117冻结指纹：61/61页、1684行。印刷35页的PDFKit CR/控制字符出现抽取形式差异，必须同时校验独立的私有行表示哈希以及冻结页指纹，而不能把不同文本编码误判为数学公式正确。

编制405条**编号/小节/开放例子编辑性来源线索**，各条都带页号、物理页号、起始行及来源行SHA-256、课程归属、数学验证待完成、教师审核待完成、不公开标记，保留来源校验与唯一ID门禁。计数分别为必修127、选择性必修89、选修A69、B70、C29、D17、E4，另选修总说明0。这个数字只是可检测的排版线索，**绝不是课程知识原子分母，也不代表已审校覆盖率**：一句话可能有多个概念/定理，带公式图片的页面存在抽取错误，有的线索只是标题。

本轮针对印刷37–50和64–73页的24页识别选修和选择性必修的章节、重要分轨边界及若干风险来源；仍不能将其标为真实教师逐页逐项审核。行级边界包括36:16选择性必修、50:20选修总体说明、51:20选修A、57:16 B、64:10 C、69:6 D、73:13 E。识别可能跨轨的页内分段，不再将某页当作单一选修轨。全部七轨官方知识原子分母仍然 **UNKNOWN/null**，教师正式原子化与审校均为0。

JSON: `curriculum/highschool_math/k00_batch118_provisional_marker_ledger.json`；文字报表：`docs/evaluation/KB_BATCH118_SOURCE_MARKER_CENSUS.md`。离线CI检查已锁定源哈希结构、候选计数及拒绝伪批准；Mac本地额外与原始合法来源重新提取结果比对，不能把离线结构检查误称为脱离来源的独立内容真值证明。

## K04 / K06：8份深度原创概率统计讲义

`scripts/kb_batch118_lessons.py`为原创内容源，`scripts/build_kb_batch118_lessons.py`负责构建强约束、Pydantic Schema、课标来源哈希映射、先修链接、校验与生成双格式。产物 `knowledge/deep/v1/batch118_probability_distribution.json` 和 `docs/evaluation/KB_BATCH118_LESSONS.md` 同步导出。8份候审单元分别为：

1. 离散随机变量的分布列（非负、和为1）。
2. 期望的线性性（不需独立）。
3. 方差恒等式与仿射缩放（尺度因子平方）。
4. 二项分布公式（独立同参；n,p及边界）。
5. 二项分布均值、方差及相关试验反例。
6. 超几何分布均值（不放回、无需独立）。
7. 正态标准化（正标准差；非正态标准化不能变正态）。
8. Pearson样本相关系数（零方差未定义、相关不等于因果）。

本批8份讲义全部配完整前提与符号、分步解释/待审证明、8项反例及错法、16道原创教师完整例题、24级学生提示和16项近远迁移。新增15条**未认证**定理证明步骤。来源链接为印刷47–48页真实对应条件线索，不把项目的旧 `HS-MATH-*` 工程ID直接当成官方原子。

历史工程待审深度稿498份，新增8份，合计506份；并**不是506个官方数学原子**。任何教师解答均保持教师侧隔离，学生权威发布0。

## K07 / K08 / K09：数学条件与安全测试

- 以SymPy/Fraction/枚举对8类内容各给出正负有限精确见证（16组）；并独立于作者原稿对16道教师例题答案单独给出精确真值检查。这样的有限代数检查不自动认证一般定理。
- 新增 `tests/test_kb_batch118.py`（61页校验、405条来源线索、14处行级分轨边界、七轨未知分母、恶意审批/错误归属/篡改来源拒绝、8篇内容Schema/先修/防剧透/学生权威负面验证）；以及 `tests/test_kb_batch118_math_oracles.py`（16例独立解答真值与10个危险反例）。
- 两个构建器以及专项测试已纳入 `scripts/mac_check.sh` 和 `.github/workflows/ci.yml`，CI本身不需要本地版权课标正文；仅Mac可额外执行 `--verify-local-source`。
- 冻结数字：所有官方正式原子总分母 UNKNOWN；教师审批0；学生端权威发布0；历史先修待审、证明未认证和数学冲突仍未清零。

## 测试、失败与修复（原始证据）

- 最早构建发现印刷35页PDFKit控制字符导致源行表示哈希不同：修复为双重指纹锁，不跳过或伪造来源校验。首次构建报告顺序受排序影响：改为显式固定七轨顺序，恢复离线严格可重复。初稿数学讲义校验发现2个太短的独立核验说明、1条论证依据不足，逐条补充后生成成功。
- 专项第一次真实执行：`563 passed`；见 `docs/evaluation/logs/KB_BATCH118_FOCUSED_FIRST.log`。
- 完整Python/Node与Chrome/Playwright复测已结束；具体退出码、数字、失败对照与日志SHA见本报告末尾「冻结源码最终验收」。


## 独立教学文字复核（首次全量测试之后新增的数学回归）

首次完整 `mac_check.sh` 在初稿下真实完成 `66,293 passed / 5 skipped`、Node `111/111`，外层退出码0；但**测试通过不能替代数学叙述审阅**。本轮随后人工检查16道教师例题的计算语句与题目条件，发现并纠正以下四处独立问题：

1. 两枚公平硬币的分布列是 `1/4, 1/2, 1/4`，原验证句错误引用了下一题的 `1/5+2/5+2/5`。原独立oracle只校验最终答案，未校验说明文本；已修复验证句并加入文本-真值一致性回归。
2. 两点等概率分布的方差例题原写成“公平骰子X只取1,3”，存在普通六面公平骰子概念冲突。已改成“随机变量X以相等概率取1、3”。
3. 六球中两枚红球、不放回取三球，原验证句错误声称红球和其他球占有相同比例；现在用每个固定球入样概率 `3/6`、两枚红球总期望 `1` 正确核查。
4. Batch118稿件因复用历史Markdown渲染函数误显示Batch117标题；现仅在本批构建输出修正标题，不更改历史Batch117冻结稿。

这些是严格的**编辑性纠错**，并未将教师审核状态变更为APPROVED。新增2项可重现负面回归；修订后专项 `565 passed / 0 failed`。最终冻结源码的全量与浏览器复测现在均已由独立 `*_FINAL` 日志和数字退出码验收。

## 下一批（依赖优先顺序）

1. 将405条仅作来源起点，逐条建立非重叠的**语义要求→概念/定理/方法原子**映射，跨页去重，审查真实原文数学公式/图像及课程目标/技能层级；分别冻结必修、选择性必修、选修A–E可审计正式分母，但真实教师核对之前均标候审。
2. 深入补齐必修数列、导数、几何与代数，选择性必修概率统计其余正态/回归/列联表、七轨不同学分要求；保持完整原创题族和独立真值验证。
3. 排查历史172条待审核先修关系、538条历史未认证证明步骤、10项数学冲突，优先修复数学前提缺失以及学生检索/挑战剧透风险。
4. 真实数学教师逐项审校、法规/版权与RAG生产发布验收未完成之前，PR保持Draft，不合并main、不关闭#17–#27、不将教学Agent转为权威模式。

## 冻结源码最终验收（MacBook Air，2026-11-13）

- 经修订的源码基线为本机 commit `24c177682b9fd2f66f09df057f01a562b34d858a`，Git tree `10fe4c159a036be6d8b1c81ab456ff36b9194e26`；最终测试期间仅生成日志和两份历史评测快照变化，不在受测源码中做运行中编辑。
- `scripts/mac_check.sh` **exit 0**：Python **66293 passed / 5 skipped / 0 failed / 1 third-party warning**，时长 1151.22s (0:19:11)；Node **111/111**，0 failed。第一份完整日志也曾 exit 0，但其后发现4处文字或检验表述问题，因此以本次冻结修复后的最终复测为准。
- `scripts/mac_browser_check.sh` **exit 0**：Chrome/Playwright交互与响应式场景通过，pytest浏览器 **2 passed**；iPad笔压是CDP仿真，不是实体Apple Pencil验证。
- 数学专项首版 **563 passed**；发现并修复四处叙述与跨批标题问题后专项 **565 passed / 0 failed**。与最终全量检查有重叠，不能相加宣称额外覆盖。有限符号真值不替代证明/教师审校。
- 受测内容仍 **REVIEW_PENDING / TEACHER_ONLY**；正式七轨知识原子分母 UNKNOWN，教师 APPROVED 0，学生权威发布0，学生自由步骤验证不得自动标记通过。
- 测试生成的两个 `evaluations/results/2026-10-15-*.json` 历史评测快照保持未暂存，不纳入交付。

### 原始日志 SHA-256

| 文件 | SHA-256 |
|---|---|
| `docs/evaluation/logs/KB_BATCH118_MAC_CHECK_FINAL.log` | `1e14050e5a907da42ddf29b32de736aacc401c5eb99d404bd24ab2f20818822e` |
| `docs/evaluation/logs/KB_BATCH118_MAC_CHECK_FINAL_EXIT.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `docs/evaluation/logs/KB_BATCH118_BROWSER_FINAL.log` | `c1edff7f2973915996c2efd711bb25941c1f06db34a85c3d10d9ba8d82aadbcc` |
| `docs/evaluation/logs/KB_BATCH118_BROWSER_FINAL_EXIT.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `docs/evaluation/logs/KB_BATCH118_MAC_CHECK_FIRST.log` | `3954a0f11aef2733cc522ab033f42a6485c6ff015480d2ee404c121d2ffb8e9e` |
| `docs/evaluation/logs/KB_BATCH118_MAC_CHECK_FIRST_EXIT.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `docs/evaluation/logs/KB_BATCH118_FOCUSED_FIRST.log` | `2e877daee41984f0c6b6b037e59958a426f6945feb2ee5fec1febcfb1b310ab2` |
| `docs/evaluation/logs/KB_BATCH118_EDITORIAL_FIX_FOCUSED.log` | `de51f5ac585c2a7b86efb31a16fcd70d53842150692d13db4bdf21faaaeb9e86` |

下一批：把405排版线索逐条按语义拆分、去重并补足公式图片审查，七轨分别统计候审分母且绝不冒充教师认证；先审历史172条先修、538条证明及10项冲突中的P0高风险样本，再扩展成组的数列/导数/统计讲义。
