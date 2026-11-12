# STEM Mentor｜Batch104 — 原创深度讲义、条件核验与课标来源结构修复（Mac-only）

> 状态：候审 Draft。此处的「通过」仅代表所列软件/有限数学实例检查，**不**代表课标原子分母已确定、数学定理已形式化证明、教师批准或学生权威发布。

## 1. 范围与源码

- 唯一开发、内容生产、数学验证与测试设备：授权 MacBook Air。
- 独立工作树：`~/Documents/文件/stem-mentor-kb-batch104`；分支 `feat/kb-batch104-deep-drafts-and-guard`；父提交为 Batch103 `1166f32141507c7cacd26b73fbf4e3e2d67bdad4`。
- 原 Mac main 的已有未提交修改原封不动；保留两份历史评测输出差异，不纳入 Git 提交。没有使用 Tang，未强推/重写/合并 main。
- 学习内容为项目原创中文草案；不上传官方教材/标准全文及真实学生数据。
- 课标参照《普通高中数学课程标准（2017年版2020年修订）》，本地原始 PDF SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。GitHub CI 仅验证版本化摘要；Mac 额外核验受许可的本地原件和 PDFKit 文本 SHA。

## 2. K02/K03/K04/K06：12份原创完整教师侧草案

新增 12 份 `DeepLesson`，包含 **5份定理、3份概念、4份方法**。每份均有正式陈述、符号、前提、应用边界、至少一个具体负例、2道分步例题、典型错因、三级提示、近迁移与远迁移。需要证明的5份定理附逐步说明与每步依据。清单：

1. 集合德摩根律与指定全集的补集（定理）
2. 充分条件与必要条件的逻辑方向（概念）
3. 负数同乘不等式必须改向（定理）
4. 二次不等式的首项符号、判别式与边界（方法）
5. 函数的单值映射、定义域与陪域（概念）
6. 分段函数接点的左右极限和函数值（方法）
7. 实对数方程的底数/真数合法域（方法）
8. SSA 非夹角的零解、一解、两解（方法）
9. 向量垂直与数量积为零的双非零条件（定理）
10. 条件概率、独立事件、互斥事件（概念）
11. 期望线性性不需要独立假设（定理）
12. 有限等比和在公比为1时的单独分支（定理）

机器审计：**12份、24个教师例题、36级分层提示、24个近远迁移任务、12个有限精确正例及12个失效前提拒绝实例、5条仅编辑草案的先修ID关系**。正式教师审核0/12，数学一般证明形式认证0/5；新增12份均 `REVIEW_PENDING` / `TEACHER_ONLY`。

合并既有目录后，当前工程工作分支共有 **405份候审深度文档（之前393 + 本批12）**。这不是405条已证实的官方独立知识原子。工程课程映射178项（必修64、选择性必修46、选修拓展68），并不等于七轨官方分母。

主要文件：
- `scripts/kb_batch104_authoring.py`
- `scripts/build_kb_batch104_deep.py`
- `backend/app/kb_batch104_oracles.py`
- `knowledge/deep/v1/batch104_core_twelve.json`
- `docs/evaluation/KB_BATCH104_TWELVE_TEACHER_LESSONS.md`
- `docs/evaluation/KB_BATCH104_DEPTH_AUDIT.json`

数学独立验证器使用 `fractions.Fraction`、整数、有限集合逐例检查。修正了失效映射、实对数域和正概率互斥这三类反例的“看似通过却没验证关键条件”的弱检查。**有限样例绝非一般定理的证明**。

## 3. K00/K01：源页13、14、51的空编号锚点归因

既有源码把这三页记作没有自动识别出的编号条款，**不能**将其解释为没有数学课程内容、已经完成全量原子化，或者需要胡乱补造知识点。

本轮在 Mac 验证原标准 PDF SHA 及三页 PDFKit 文本哈希，建立 **3页、76条PDFKit文本行、12个连续且无重叠来源结构区段** 的原创语义解释。表格课时、栏目/页码、课程定位和数学要求必须分型；第14页的预备知识导言跨入后续页，第51页的选修A微积分起始跨入第52页，两者保持 `CROSS_PAGE_REVIEW_PENDING`。

- 第13页：必修课程概要、课时目录、页尾；
- 第14页：续表、主题内容目录、预备知识章节开篇、页尾；
- 第51页：选修通用定位、A–E差异、课程评价、A轨专题转换、微积分跨页内容。

页内区段拥有 PDF SHA、PDFKit 页 SHA、页号、行区间、轨道、原创释义。**全七轨正式课程原子分母均为 UNKNOWN**；教师逐页完整原子化依旧0/61。

主要文件：
- `scripts/build_kb_batch104_source_structure.py`
- `docs/evaluation/KB_BATCH104_SOURCE_PAGES_13_14_51.json`
- `docs/evaluation/KB_BATCH104_SOURCE_PAGES_13_14_51.md`

## 4. K09 回归与原始证据

- 新增 `backend/tests/test_kb_batch104_teacher_depth.py`、`backend/tests/test_kb_batch104_source_structure.py`，重点拦截：虚假教师签字、非法知识类型、假先修边、自环/循环/孤儿、少量例题、假通用证明、伪造官方覆盖率、越界/重复/漏报 PDFKit 行区间、跨轨目录误认、学生检索剧透。
- 单独跑本批专项：**69 passed**（包含来源结构专项）；其中 Mac 原 PDF 检查确实执行。GitHub CI 因无本地受许可 PDF 会 skip 3个纯本地 PDF 案例，但仍执行版本化文件哈希和结构负面测试。
- 把两份构建器的 `--check` 加入 Mac 本地脚本及 GitHub Actions；Mac 的源文检查同时启用 `--verify-local-source`。
- 完整 Python/Node/browser 真实测试和退出码见下方最终结果；所有原始日志均入库，不能从旧批次推测成功。

**最终 Mac 验收（真实运行）：** `scripts/mac_check.sh` 退出码 **0**；Python 全量 **64,139 passed, 5 skipped, 1 warning**, 0 failed，运行 1062.22 秒；Node **111/111 passed**；Chrome/Playwright 检查通过，浏览器 pytest **2 passed**；新增 Batch104 专项 **69 passed**（包含于 Python 全量数量，不重复累计）。测试为 Mac 原生执行，不代表教师签审或无限域定理形式证明。

- 源码可复现性：`build_kb_batch104_deep.py --check` 通过；`build_kb_batch104_source_structure.py --check --verify-local-source` 通过。
- 新增专项记录：`docs/evaluation/logs/KB_BATCH104_69_FOCUSED.log`。
- 原始全量日志：`docs/evaluation/logs/KB_BATCH104_MAC_CHECK_FINAL.log`（此前一次全量记录另归档为 `KB_BATCH104_MAC_CHECK_PRE_SOURCE_AUDIT.log`）。
- 浏览器运行记录：`docs/evaluation/logs/KB_BATCH104_BROWSER_CHECK.log`。
- 测试核心 Commit：ada083f77c257a9f43e00e841763d057ce08c20e；源码 Tree：37d4b8306540046748be82878e336648453621a6；最终远端交付另以 PR 的 HEAD 为准。

## 5. 未满足门槛与下一批

1. 正式课标七轨的知识原子分母仍全部 UNKNOWN。第13/14/51页结构分类不等于逐页教师确认。下一批应跨页联读14–15、51–52，继续独立审核其他无编号条款与完整教研原子化。
2. 尚有74个临时工程主题未做成对语义审查；但300个内部主题不是官方分母。
3. 历史172条文本先修仍未经完整人工语义审核和正式ID绑定；本批5条只在候审草案内部可用，不提升为学生权威路径。
4. 历史538个证明步骤未完成通用证明核验，10个内容冲突待独立裁决。
5. 未有教师签名审核，因此当前**教师 APPROVED=0，学生权威发布=0**。后续扩展到完整选修A–E和所有必修、选择性必修模块，不得将运行软件测试等同教学质量。

## 6. 交付边界

仅在本地真实修改、Mac执行并记录完整测试后，提交独立分支并创建 Draft PR；GitHub 是唯一提交事实源。PR保持 Draft，GitHub CI须独立通过，且教师审核必须真实发生后才允许权威发布。

## 7. 版本化原始日志 SHA-256

| 文件 | SHA-256 |
|---|---|
| `docs/evaluation/logs/KB_BATCH104_69_FOCUSED.log` | `2817ef4419335538efe3a748d21de6dc8efe2acf961286b7e4e1ac1d747d77a7` |
| `docs/evaluation/logs/KB_BATCH104_BROWSER_CHECK.log` | `1578804bd5957a3f5e9a5639b46b17ea87a2a662fc8d772038155113035376d8` |
| `docs/evaluation/logs/KB_BATCH104_MAC_CHECK_FINAL.log` | `da31e31ac1da3a54a8b27072837f51eefa10fcf6c8d28a371b99e38bfb36cd6a` |
| `docs/evaluation/logs/KB_BATCH104_MAC_CHECK_PRE_SOURCE_AUDIT.log` | `78aed07eed6efd90668ae023497e32284d65bdfa23799a290ad4a9d005286979` |
