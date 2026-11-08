# STEM Mentor｜Batch26 实际执行与验收（2026-11-08）

## 1. 环境、保护与基线

- 唯一开发、内容生产和测试设备：授权 **MacBook Air**。未在 Tang 上进行任何知识库开发。
- 独立 worktree：`~/Documents/文件/stem-mentor-kb-batch26`，分支 `feat/kb-batch26-prereq-audit-atomic-scope`。
- 远端继承基线：Batch25 Draft PR #51，GitHub commit `0c0f927cdce0b16c72a1903f38e1ac84afa6b327`。基于 Batch25 feature branch 堆叠 Draft，不合并 main、不推送主分支；主项目工作树原有 11 项未提交修改保持不动。
- 本批不新增所谓“完整讲义”数量；解决**官方课标可复现证据版本漂移**和**缺失先修图的编辑审核**两项之前没有量化闭环的高价值依赖问题。GitHub #17–#27 仍保持 OPEN。

## 2. K00：61 页真实官方 PDF 的独立重新抽取与差异审计

Mac 从课程标准发布来源下载原始 PDF，仅保存于本机临时目录 `/tmp/stemmentor-official-batch26/standard.pdf`，**未纳入 GitHub**。实际下载文件 SHA256：

```
cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195
```

出版资料：教育部《普通高中数学课程标准（2017 年版 2020 年修订）》，人民教育出版社发布的 PDF；源 URL 存于历史审计账本 `curriculum/highschool_math/official_numbered_clause_evidence_batch18.json`。PDF 共 188 页，本批在印刷页 13–73 共 61 页执行**机器重抽取**。内容不复制课标全文，提交的仅是位置、标记、源页哈希和审计元数据。

| 提取方案 | 必修标记 | 选择性必修标记 | 选修 A | 选修 B | 选修 C | D/E | 合计 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Batch18 冻结账本 | 114 | 82 | 52 | 51 | 16 | 0 | **315** |
| Mac `pypdf==5.9.0` 原 PDF 重抽取 | 114 | 82 | 54 | 51 | 16 | 0 | **317** |
| Mac `pypdf==6.5.0` 独立版本复验 | 114 | 82 | 54 | 51 | 16 | 0 | **317** |

`pypdf==5.9.0` 与 `6.5.0` 在本次机器上的 JSON 输出 **字节一致**。较旧 `pypdf==3.17.4` 同一提取算法得到 121 个标记，证明原始文字流高度依赖解析器版本。与冻结 Batch18 账本相比，最新抽取 **61/61 页文字哈希不同，编号标记数量仅印刷页 52 多出两次**；不能未经视觉核对就认为“多出两个官方知识点”。这些是**编号标记出现次数，不是原子知识能力分母**，仍可能有行续接、条款复合、表格、无编号要求或重复。

新增：
- `curriculum/highschool_math/official_pypdf59_reextract_batch26.json`：317 次标记的位置/行哈希，保留全部七轨、没有版权正文；
- `scripts/build_kb_batch26_source_reextract.py`：校验原 PDF 固定 SHA、两个账本的完整字节哈希、61 页顺序及 PDF 索引、编号轨道和伪教师审核；`--check` 在 CI 不下载 PDF，`--pdf ... --check` 可在 Mac 验证官方原字节并重放抽取；
- `docs/evaluation/KB_BATCH26_K00_PDF_REEXTRACTION_AUDIT.json`：**逐页 61 行**差异矩阵，专门暴露 52 页异动和每页文本哈希差异。

严格事实边界：**已机器重新解析的页为 61，人工对照原页图/公式/表格的完整核对为 0。** Batch25 20 页无编号、23 页高密度编号和全部 D/E 非编号章节仍需审核。正式七条课程轨官方原子分母、正式覆盖率仍均为 `null`；真实教师批准 0。尤其 315、317、132 自编目标、23 选修主题不能相加冒充课标总量。

## 3. K01/K06/K08：31 项原创先修关系候选与无剧透编辑检索

此前 287 篇草案中 **133 篇没有显式先修知识图边**。本批手工逐条审视相应题目，原创编写 **31 条具体先修关系候选**，分别给出知识 ID、依赖知识 ID 及中文数学先修必要性。例如“奇偶函数定义域对称”需先理解函数定义域；“SSA 多解”先理解正弦定理；“条件概率/独立判定”先理解条件概率的非零分母；“含参数二次不等式”先理解判别式及根存在性。均是**编辑提议，非数学证明认证**。

新增：
- `knowledge/deep/prerequisite_editorial_candidates_batch26.json`：31 个待教师审定的有向边提议，均 `PENDING`，没有伪造签名。
- `backend/app/kb_batch26_graph.py`：检查合法 lesson IDs、无孤儿/自环/重复边、组合旧图后仍为 DAG、不得附教师签名、不得标成已上课使用。
- `scripts/build_kb_batch26_graph_progress.py` 和 `docs/evaluation/KB_BATCH26_PREREQUISITE_EDITORIAL_REVIEW.json`：输出机器可追踪的 **133 项全量未连图草案队列**；31 项目前有编辑候选，**102 项仍没有候选**。
- `backend/app/deep_retrieval.py`：只在既有 `editor_draft_full(...,scope="EDITOR_LOCAL")` 编辑预览中附带这些提议；学生端 `student_evidence_lookup` 保持原有 fail-closed `NO_APPROVED_EVIDENCE`，不接触教师完整解答或待审边。编辑 `scope` 只是误用保护，不是正式身份鉴权，不可直接注册为 HTTP API。
- 新增 JSON 快照重算和负面回归 `backend/tests/test_kb_batch26_source_graph.py`，并把两个可复现 `--check` 门禁接入 GitHub Actions 与 Mac 测试脚本。

**未改变**任何 `knowledge/deep/v1/*.json` 权威课程的 `prerequisite_lesson_ids` 字段，不造假“133 篇已修复”，31 项仍待老师审核和全课程严格关联审查。

## 4. Mac 真实测试与版本化证据

测试产物：`evaluations/results/2026-11-08-kb-batch26/`。

- 完整 Mac 脚本 `bash scripts/mac_check.sh`：**EXIT 0**；包含全部原有数学/来源/审核生成器门禁及本批新增两项。
- 后端全量 Python：首次 **25,232 passed，0 failed，1 条 anyio/Starlette 弃用告警**；脚本和回归再校正后重新执行全量，**25,233 passed，0 failed，1 warning**，终态日志 `python-final.log`。
- 本批新专项：**123 passed，0 failed**。涵盖七轨、61 页、31 条编辑边、反事实/非法哈希/伪签名、循环及孤儿先修和学生无剧透。
- Node 单元测试 **111/111 passed**；模拟教学策略 **33/33 passed**；检索困难负例 **40/40 passed**，Top3 **22/22**。
- Chrome 完整浏览器脚本 **15 组执行成功，最终额外浏览器 pytest 2 passed**，`scripts/mac_browser_check.sh` **EXIT 0**；随机端口、合成临时数据库，无真实学生数据、没有外部服务请求。已有场景覆盖函数、概率、数列、几何实验室、iPad 笔触模拟（非物理设备测试）。
- 课标原 PDF SHA 与双解析器复验：`source-reextraction.log`；脚本与报告快照校验全部通过。

测试仅确认软件逻辑和受控边界，不等于官方数学课标最终识别、定理整体验证或真人教师批准。任何学生自由解题步骤仍未认证。

## 5. 仍然开放的全量验收缺口与下批

- 工程主题 178、结构化深度草案 **287**（本批新增 0）、教师侧例题 574、自然语言证明步骤未形式认证 **538**。
- 历史 P0 高风险 **127** 条、历史内容冲突 **10** 组，**均未自动关闭**。
- 教师真正批准 **0**，学生端正式深度讲义发布 **0**。
- 官方课标知识原子分母：必修、选择性必修、选修 A–E **全部未核准**，正式覆盖率 `null`。

**下一批依赖顺序**：
1. K00：对印刷第 **52 页**新增的两个编号位置做独立原始页图文/上下文审查，同时核对 20 页无编号和 23 页高密度要求，显式拆成可审核原子候选，保留跨解析器异同；课标范围冻结后才允许宣称官方分母。
2. K07：从 127 条 P0 证明步骤选出分母、定义域、退化三角形/几何条件逐条建立有效前提、反例与独立数学证据；10 组冲突只有经独立数学裁决才标为已解决。
3. K01/K06：31 条先修编辑候选接受逐项内容关联、必要性、环风险核实；继续研究其余 102 项是基础根节点或需要新增真实前置讲义，不能为了图连通强制附边。
4. K02–K05：恢复成组补齐必修与选择性必修实际课程原子完整讲义、题族和 near/far 迁移；K08/K09 持续测教学 Agent 只引用经过签署批准的内容及不泄漏教师完整解答。

**GitHub 审查界限**：本批来源是教育部公开课标的页号及哈希、手工原创审查逻辑与数学链接关系，无原 PDF、无教材正文、无学生真实数据。分支保持 Draft PR；不合并 main，不发布未经教师批准的内容。

## 6. 已核实的源码/远端证据

- 上游 GitHub 起点：`0c0f927cdce0b16c72a1903f38e1ac84afa6b327`（Draft PR #51）。
- Mac 已实际跑过全量后端/Node/策略/检索/浏览器测试的本批**源码与日志提交**：`7904ac9963a27cd179dadb77640da9ae2f4e142b`；Git tree：`ce87cf0ba027989959c844a35d73ca8711b9ae45`。最后的 `python-final.log` 确认 `25233 passed, 1 warning`，`browser.log` 记录 Chrome 脚本和浏览器 pytest 终态 `EXIT=0`。
- GitHub `git push` 已实际成功，无需调用替代推送接口；推送证据 `evaluations/results/2026-11-08-kb-batch26/git-push.log`。
- 远端 Draft PR [#52](https://github.com/YOUessi/stem-mentor/pull/52) 基于 Batch25 feature 分支，不合并 main；本次源码 HEAD 在 GitHub Actions [#42436061579](https://github.com/YOUessi/stem-mentor/actions/runs/42436061579) **completed / success**。该 CI 是软件正确性验证，**不是数学形式证明和真实教师签署**。
- 后续若仅新增记录本节的纯文档/日志 commit，应单独核实其 CI；已测试的源码树保持不变。所有 GitHub Issues #17–#27 的真正最终完成门槛依旧未满足。
