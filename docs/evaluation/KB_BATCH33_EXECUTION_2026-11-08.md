# STEM Mentor｜Batch33 Mac 源码开发与验收

日期：2026-11-08。**唯一源码生产/测试设备：授权 YOUTangdeMacBook-Air.local**。独立 worktree 为 `~/Documents/文件/stem-mentor-kb-batch33`，分支 `feat/kb-batch33-elective-scope-mapping`，基于 Batch32 本地 commit `92c82476458d6dbae84dc2581ea7af09d5ef761e`（tree `757c9517106c50e66c119c86a700ded3a031a6c4`），与 GitHub 上 Draft PR #57 最终远端代码树一致。Mac 主仓原有 11 项未提交修改均未触碰；Tang 未用于研发。未修改、重写或合并 main。

## K00：课标原版范围首次全文页级内容检查

- 在 Mac 确认原始《普通高中数学课程标准（2017 年版 2020 年修订）》共 188 个 PDF 页，文件原版 SHA256：`cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。原 PDF **不上传至代码仓库**；无需复制版权原文。
- 使用 macOS **PDFKit + CryptoKit SHA256** 新读取并审阅印刷第 13、14、51–73 页的文本（25 页；第 51–73 共 23 页）。因前批已经看过印刷第 52 页并做视觉核对，所以新增**此前完全没有内容初查的页面 24 页**；联合先前 37 页，课标范围**61/61 页经过至少初步文本/版面检查**。原始 Mac PDFKit 页级摘要固定于 `scripts/build_kb_batch33_elective_scope.py`；使用 `--pdf` 与 `--pdfkit-digests` 可原地重验。
- 这**不是官方知识原子分母已经完整**：61/61 页还**没有**完成“每一条编号及未编号要求”逐句分解、归属及人工复核，第 35 页图像文字乱码仍需要独立版面检查，选修 E 属于学校可开发的开放内容，不能制造一个全国统一固定分母。
- 新增 96 条项目**原创单技能候选**，选修 A 28、B 29、C 19、D 16、E 4；文件 `curriculum/highschool_math/k00_batch33_elective_editorial.tsv`，SHA256 `ad5b47d8aac24142ed5256eb238fad31256892c3ce65b2b6d70b512d99e5e7c4`。每条有源页、项目原创目标、课程类型、来源文本哈希、审核 pending、官方条目 ID null 和学生不可见标记。A/B/C/D 跨页混合边界 57/64/69/73 有精确主题拒绝门禁。E 的四个是选择性拓展例子，不是必修目标。
- 与 Batch31/32 217 个候选合计 **313 个编辑候选**：必修 125、选择性必修 92、选修 A 28/B 29/C 19/D 16/E 4。**313 与 315/317 个提取编号标记均不能被用作官方原子分母。所有七条轨道正式分母及覆盖率仍然 null。**
- 生成的机器审计文件：`docs/evaluation/KB_BATCH33_ELECTIVE_SCOPE_AUDIT.json`；全部页级内容审查与逐条条款校核的差异保持可见。

## K01/K05：已有深度草稿与 96 项选修候选的审查关系

- 直接解析 `knowledge/deep/v1/*.json`，核对原有 **287 篇**结构化讲义的唯一 ID、`REVIEW_PENDING` 状态、`TEACHER_ONLY` 完整解答控制。原深度讲义未增减，不伪称 96 个原子候选已变成讲义。
- 原创编辑关联 TSV `curriculum/highschool_math/k00_batch33_draft_associations.tsv` 共 **47 条逐项数学关系建议**，A16/B12/C9/D7/E3；对每个候选 ID 指向确有的知识讲义 ID，给出为什么与此候选相关、哪些范围未覆盖的理由。**49 条本批候选还未建立任何草稿关系建议**。关联只是人工审核线索，不是自动字面相关、内容等价证明，更不是课程覆盖率。
- 构建器 `scripts/build_kb_batch33_draft_crosswalk.py` 与审核报告 `docs/evaluation/KB_BATCH33_DRAFT_CROSSWALK_AUDIT.json`；拒绝重复 ID、已删除讲义 ID、无效关联、伪批准、短理由等负例。尚未把建议挂接到学生权威先修图或学生 RAG/API。

## K07：五项相互独立的有限数学判定工具

- 新增 `backend/app/kb_batch33_elective_finite_math.py`、`knowledge/proof/kb_batch33_elective_finite_fixtures.json`、`scripts/build_kb_batch33_math_finite_audit.py` 及报告 `docs/evaluation/KB_BATCH33_FINITE_MATH_AUDIT.json`。
- 五项分别为：一阶仿射差分方程有限迭代/闭式核对（a=1 单独处理）、正增长因子复利模型、正整数节拍周期同步最小公倍数、二维正交矩阵内积/长度不变量及行列式符号、可逆 2×2 系统的唯一解与回代。**5 个有效有限实例通过 + 5 个非法前提被明确拒绝**。受限 Fraction 输入严格拒绝不可信字符串、负维度、零分母、矩阵退化或超出有界数值输入。
- 原创逐步计算、定理前提、失效反例、常见错因及近远迁移见 `docs/evaluation/KB_BATCH33_MATH_DERIVATIONS_AND_COUNTEREXAMPLES.md`；仅为教师审核草案。没有通用定理形式证明证书、没有为学生自由文本判题、没有教师签字。
- 新增独立专项 `backend/tests/test_kb_batch33_elective_scope_crosswalk.py`：全体 96 个候选的范围与非授权检查、61 页元数据检查、47 条无剧透关联建议、跨页错归属/伪审核/来源替换/计算失效反例、大量有理数精确参数网格测试。**1,307 passed，0 failed**（Mac 日志 `evaluations/results/2026-11-08-kb-batch33/targeted-initial.log`）。
- 原先 `scripts/build_kb_batch33_draft_crosswalk.py` 初次生成校验拒绝一批简洁但有意义的中文关系说明（英文字符数阈值太高），校对后将理由的最短长度从 25 修至 14，同时保留数学关系说明与原文件 SHA 锚定；最终 47 条有效，无数学覆盖误判。

## K09：真实 Mac 回归及 CI 门禁

- macOS `bash scripts/mac_check.sh` 已运行完整后端、Node、教学策略与检索，不只运行新专项；加入 Batch33 **3 项受审计的构建 --check 门禁**，GitHub Actions 的 Ubuntu CI 也加入同一检查。
- Python **36,979 passed，0 failed，1 条第三方依赖 warning**，耗时约 110.77 秒；Node **111 passed，0 failed**；教学策略 **33/33 通过**；检索困难负例 **40/40 通过**、Top3 **22/22**；全部 CI 生成/检查逻辑最终通过；Mac 复验退出码 **0**。原始日志 `evaluations/results/2026-11-08-kb-batch33/mac-check.log`。
- 运行教学策略/检索脚本生成的旧 `evaluations/results/2026-10-15-*.json` 仅在本独立工作树内恢复到原状态，没有污染原主仓、其他分支或修改先前冻结结论。
- Chrome + Playwright 全套脚本回归 **15 个脚本通过，0 失败**，浏览器 pytest **2 passed**，最终 **BROWSER_EXIT=0**。日志在 evaluations/results/2026-11-08-kb-batch33/browser.log。测试使用临时合成数据库，不调用外部 API，不产生真实学生记录；iPad 手写/笔压是 CDP pointer 仿真，**不是物理设备**或真实学习增益验收。
- 当前 **287** 篇深度讲义均待真人教师审核；**538** 条原有自然语言证明步骤未形式认证，历史 P0 **127 条**为审核备忘而非形式证书，**10 组**冲突未正式裁决；教师正式批准 **0**、学生正式深度内容发布 **0**。教学 Agent 的权威内容发布门禁未修改，所有本批新增数据仍停留编辑/审核阶段。

## GitHub 来源事实与后续开发

- 新源码所有修改均在 Mac 的独立 feature branch / worktree；Mac 已完成源码验证提交 b267f23d1dbfebd8bcdbd57cd6c457ac10ec82d4，源码 Git Tree fb6a861d85cff39b55c33ff0c816bbec015eb87e，已经独立在 GitHub 回读。Draft PR #58：https://github.com/YOUessi/stem-mentor/pull/58 （base 为 Batch32 feature branch，未合并 main）。源码提交 Actions #42456397894（https://github.com/YOUessi/stem-mentor/actions/runs/42456397894）已核实为 SUCCESS。后续提交浏览器证据和执行报告仍须再次核对最终 HEAD 和 CI，不把旧 Success 冒充新提交成功。
- 下一批优先项：对 61 页逐句审查全部编号与未编号课标要求，并独立看第 35 页 PDFKit 图形；为全七轨道建立经教师核对的原子分母和可计算覆盖矩阵；逐项审核 47 条候选关联，优先为剩余 49 项无关联候选补足原创完整讲义及题族；推进 538 条证明的形式/人工认证及 10 组冲突；验证真实 API/Agent 防剧透和未见题；必须拿到真实教师审核才能发布，所有 Issues 保持 OPEN。
