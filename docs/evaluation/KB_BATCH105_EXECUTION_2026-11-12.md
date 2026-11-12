# STEM Mentor｜Batch105 课标跨页候选原子审查：Mac 实际验收记录

> 交付状态：GitHub [Draft PR #130](https://github.com/YOUessi/stem-mentor/pull/130)。`REVIEW_PENDING`，非教师批准、非全量官方课标原子，也非通用形式证明。独立 CI 结果以 GitHub Actions 实时状态为准。

## 1. 源码和设备事实

- 唯一开发/测试：MacBook Air `YOUTangdeMacBook-Air.local`，独立工作树 `~/Documents/文件/stem-mentor-kb-batch105`，分支 `feat/kb-batch105-official-cross-page-atoms`；Python Python 3.13.13，Node v22.23.1。
- 开发原提交 `13dd2de2610966b51536072be4e53ce5f6a6ce92`，源码 Tree `1b1ab3055b159265bd2e5f73fe721a2f3acd48e0`。远端第一次交付提交 `986576ec819eaabc98e1f942e4551a2b2573da25`，两者源码树一致；后续本报告/日志形成单独交付增量，最终 GitHub SHA 以 PR head 为准。
- Mac 原主仓脏工作树原样保留；测试产生的两份历史评测快照修改未暂存、不属于本次提交。没有使用 Tang、没有强推、没有重写/合并 main。
- 本地原始 2020 普通高中数学课程标准 PDF SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`；Mac 本地额外按 PDFKit 页面文本哈希核验。只提交页码、行坐标、SHA及原创解释，不上传版权 PDF 或真实学生数据。

## 2. 本批可核实的知识成果

- K00：跨印刷页14→15（必修集合）和51→52（选修A极限）建立**2条跨页结构关联**，对印刷页15（27行）与52（49行）建立**10个无漏行、无重叠的来源结构段**，合计76行。
- K00/K01：独立形成**17条原创可追溯数学要求候选**（COMPULSORY 8、ELECTIVE_A 9），每项都有数学条件、误用/泛化反例、候审来源区间及可选的现有讲义关联。全部 `REVIEW_PENDING`、`official_atom_id=null`、`publishable_for_student=false`；不是17个教师认证的官方知识原子，也不是新增17份完整教学讲义。
- K07：每条候选对应一组**独立精确有限集合/有理数/SymPy极限见证**，并拒绝一条失效泛化；只验证所列样例，不证明所有实数及任意学生推理步骤。
- K01/K09：构建器在 CI 与 Mac `--check` 中验证可复现构建、来源 SHA、行段无缺口、七轨归属、相关候审讲义真实 ID、非法批准/官方 ID 拒绝及源文件漂移。
- K08：候选未挂学生权威检索索引；教师解答仍不进入学生自主挑战检索。现有405份工程候审深度文档不等于405个官方课标知识原子。

新增主要文件：`scripts/kb_batch105_crosspage_authoring.py`、`scripts/build_kb_batch105_crosspage_atoms.py`、`backend/app/kb_batch105_math.py`、`backend/tests/test_kb_batch105_crosspage_atoms.py`、`docs/evaluation/KB_BATCH105_CROSSPAGE_ATOMS.json` 及同名 Markdown；同步更新 Mac/CI 构建检查。

## 3. Mac 实测回归（不重复累计专项数）

- 本批专项：**109 passed / 0 failed**。使用 ` .venv/bin/python -m pytest -q backend/tests/test_kb_batch105_crosspage_atoms.py` 真实复测。
- 全量 `bash scripts/mac_check.sh`：**退出码0**；Python **64,248 passed、5 skipped、1 warning、0 failed**（1,200.63秒）；Node **111/111 passed**；模拟策略、结构检索负例、前端语法及全量构建检查都在该脚本内执行。
- Chrome/Playwright 检查通过；独立浏览器 pytest **2 passed**，脚本覆盖不同视口、MathLab边界、iPad指针模拟等；不冒称实体 iPad 测试。
- `--verify-local-source` 通过的证据只在授权 Mac 保留原件时成立；CI 环境不会错误声称见过 PDF 原件。

## 4. 原始测试日志 SHA-256

| 仓库路径 | SHA-256 |
|---|---|
| `docs/evaluation/logs/KB_BATCH105_109_FOCUSED_FINAL.log` | `a213d12e9c6358d6e85548825021b69d797d78afafae646687e384cc635e6848` |
| `docs/evaluation/logs/KB_BATCH105_MAC_BROWSER_FINAL.log` | `a80c740ea698058a0d1e39226534ba2077597a21b630d329dc92f74843e5e096` |
| `docs/evaluation/logs/KB_BATCH105_MAC_CHECK_FINAL.log` | `0d1f38582fa03d767d9c674e6ad05d835f0867828afc8a743b16e10629faefa2` |

## 5. 剩余阻断和下一批

- 官方必修、选择性必修、选修A–E **七轨正式知识原子分母仍全部未知**；完整教师逐页原子化仍为0/61页。不得以17个候选、300个临时主题或405份工程文档冒充官方分母。
- 74个内部临时标签未完成成对数学语义比较；172条历史文本先修尚未正式审核绑定；538条历史证明步骤未认证；10项内容冲突尚未关闭。
- 教师 APPROVED=0、学生权威发布=0。符号见证/CI通过不赋予教师审查权限。
- 下一批从第15→16页、第52→53页及未覆盖61页的结构来源继续拆分正式候选，并追加跨页边界失效负测。并行建设20–30份真正有定义/前提/推导/题族/错因/提示的完整原创讲义，逐章对应七轨分母；优先修复先修图谱的未认证边而非盲目提升计数。
