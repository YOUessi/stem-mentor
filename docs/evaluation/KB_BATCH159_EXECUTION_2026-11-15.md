# STEM Mentor · KB Batch159｜Mac 真实开发、数学与发布门禁记录

**执行设备**：授权 `YOUTangdeMacBook-Air.local`（唯一代码和内容生产、测试环境）；没有在 Tang 开发。
**独立工作树**：`~/Documents/文件/stem-mentor-kb-batch159`；特性分支 `feat/kb-batch159-semantic-atom-ledger`。
**源代码提交**：`fd10511c80d284a72be11fcc936a310704271603`（此 SHA 绑定实际新讲义/索引/数学校验器）；证据归档作为后续单独提交，不采用自引用提交哈希。
**审查 PR**：[Draft #184](https://github.com/YOUessi/stem-mentor/pull/184)，基于 KB158 `784b1ae313dea03cf37fc8fc6a426fa27678de07`，绝不自动合并 `main`。

## 1. 本批明确增加的原创内容（K02、K03、K05、K06）

新增10个相互关联的**必修函数模块完整教师候审稿**：

1. 函数的解析式、表格与图像三表征及信息损失；
2. 指数函数底数限制、严格单调性与图像取值域；
3. 实对数函数的定义域、互逆表示与单调方向；
4. 指数与对数互逆的双射条件与两个合成恒等式；
5. 正弦余弦主周期图像及正切极点的定义域分割；
6. 非退化正弦模型的振幅、周期、相位及物理量纲；
7. 余弦差角公式的单位向量内积推导与无分母边界；
8. 正弦和差角联立得到积化和差的无除零恒等式；
9. 函数零点、方程实根与图像交轴点的等价条件；
10. 现实函数建模的变量定义、量纲、边界及失效检验。

每稿提供正式陈述、域和量词/适用条件、四段理由、反例、不合法方法、错误修复、**2道教师完整例题**、**3层不剧透学生提示**和近/远变式。累计新增20道教师例题、30层提示和20项迁移。源稿：`knowledge/editorial_review/kb_batch159_ten_teacher_lessons.json`，逐篇人工易读版本：`docs/evaluation/KB_BATCH159_FUNCTIONS_CHAPTER.md`；10份 `knowledge/editorial_review/kb_batch159_ten_authoring.jsonl` 为原创编辑素材。

全部保持 `REVIEW_PENDING / TEACHER_ONLY`，**不是教师认可、不是已认证定理，也不向学生直接提供完整解答**。

## 2. K00/K01 机器可审计事实边界

- Mac 原始 PDFKit 的来源页、行及 SHA-256 经重放核验，来源锁存在 `kb_batch159_source_line_sha256.json`；未提交受限原始PDF或课标大段文本。
- 本批增加10份候选语义档案、先修依赖提案与重叠审查队列。候选 `c503/c504`、`c507/旧c409` 均**只标记待语义裁决**，没有自动合并或计入官方课程原子。
- 已有深度候审讲义从175增至**185**，七轨分布：必修76、选择性必修38、选修A21、B13、C13、D13、E11。历史239条编辑线索中144条关联候审稿、95条仍无；这既不是教学审核覆盖率，也不是课标分母。
- 315条编号**版式来源标记**与课程知识原子不同。必修、选择性必修和选修A–E的正式官方原子分母**全部 UNKNOWN**，因此全国课程覆盖率**不可计算**。教师批准0，学生权威发布0。完整度数据见 `KB_BATCH159_DEPTH_AUDIT.json` 与 `KB_BATCH159_PROVISIONAL_ATOM_DOSSIERS.json`。

## 3. K07/K08/K09 数学条件、检索和权限

- `scripts/check_kb_batch159_math.py` 对20道教师例题执行独立的有限SymPy/精确有理数结果校验，对20个失效前提/错误泛化给出精确反见证：**40/40 PASS**。包含负底数实指数、真数非正、正切极点、零振幅、二重根不变号、约分排除点及物理单位等。**这些是有限见证，非一般形式化证明，也没有验证学生任意自然语言解题。**
- `backend/app/kb_batch159_index.py` 建立185份候审稿的本地教师编辑索引；普通学生查找未批准证据得到 `NO_APPROVED_EVIDENCE`。编辑索引不存储教师完整解答；聚合接口 `/api/knowledge/kb159-review-coverage` 不返回敏感题解或原始正文。
- `.github/workflows/ci.yml` 运行 Linux 可核查的来源快照、exact-guard、聚合权限测试与证据SHA/伪造日志回归。Mac 私有原始来源重放在 Mac 本地执行，不冒充Linux上可访问原始PDF。

## 4. 已真实执行的 Mac 验收（原始stdout、退出码均已保存）

| 实际执行 | 结果 | 事实边界 |
|---|---|---|
| `PYTHONPATH=backend:. .venv/bin/python -m pytest -q backend/tests/test_kb_batch159_functions.py` | **125 passed**, 1个第三方弃用警告 | 不等于单独新增125个独立断言 |
| `.venv/bin/python scripts/build_kb_batch159_functions.py --check-mac` | **PASS，退出0** | Mac 私有原始PDFKit来源行哈希重算 |
| `.venv/bin/python scripts/check_kb_batch159_math.py --check` | **40/40有限见证通过** | 20正向教师例题＋20失效前提；不是一般定理证明 |
| Chrome/Playwright与浏览器pytest | **9组iPad模拟交互＋2 passed，退出0** | 不是实体iPad测试 |
| `bash scripts/mac_check.sh` | **EXIT 0**：Python后端 **66,418 passed，5 skipped**，Node **111 passed，0 failed**，其余增量/项目测试通过 | 全量内包含多个专项，禁止与专项叠加冒充独立例数；Python用时18分38秒 |
| `PYTHONPATH=backend:. .venv/bin/python -m pytest -q tests/test_kb_batch159_archive.py` | **26 passed，退出0** | 实际日志归档与伪造输入负面测试 |
| `PYTHONPATH=backend:. .venv/bin/python -m pytest -q backend/tests/test_kb_batch159_functions.py tests/test_kb_batch159_archive.py` | **151 passed，1 warning，退出0** | 同一轮联合回归，与125、26重叠 |

五组主验收stdout/exit以 `docs/evaluation/kb159_logs/` 保存，并由 `KB_BATCH159_TEST_MANIFEST.json` 逐文件记录SHA-256和退出码；`.venv/bin/python scripts/build_kb_batch159_execution_manifest.py --check` 逐字节重放。archive QA及联合回归原始日志另行保存。

**发现并修复的真实失败**：首次执行新增归档负面测试出现**16 failed / 10 passed**；原因是复制到pytest临时目录的日志被错误地调用 `relative_to(repo_root)`，导致某些案例测试在哈希/退出码检查前崩溃。改为在Manifest记录固定的仓库归档相对路径、对临时副本进行原地内容校验后，26/26通过，联合151/151通过。首次失败的完整stdout未独立归档，**不能称为已留存原始失败日志**；复现与修复可在本提交的代码及测试中审查。

## 5. 防护、遗留与下一批

**保护**：主仓未提交内容完全未触动；Mac全量检查自动产生的两份 `evaluations/results/2026-10-15-*.json` 修改没有放入本PR；没有强推、合并main、碰Tang、发布学生数据、上传版权教材全文或伪造教师批准。

**尚未验收**：正式七轨课标原子分母（跨页语义去重、选修D/E非编号要求及来源人工判定）、95条历史候选缺乏对应深度讲义、538个历史未获一般形式认证的证明步骤、10个待裁决数学冲突、真实教师签字、冻结的未见题API与规则基线对比（条件正确、泄漏、拒答、成本、P95）。

**建议下一批**：从真实课标页与历史候选做成组语义裁决并冻结**部分已审校的官方原子**，将剩余缺口按必修/选择性必修/选修A–E拆分统计；优先处理K07条件错误高风险的冲突；选一整个概率/几何模块继续原创深度讲义，冻结一批未见题并对FTS/规则/真实API分别验收。任何未经真实教师裁决的内容仍为待审稿，PR始终Draft。
